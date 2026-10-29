"""Exercise clone updates and workspace ownership using temporary local repositories."""

import fcntl
import json
import os
import runpy
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "setup.py"


class SetupTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="devhub-setup-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.workspace = self.root / "personal workspace"
        self.workspace.mkdir()
        self.source = self.root / "upstream"
        self.source.mkdir()
        self.home = self.root / "home"
        self.home.mkdir()
        self.env = dict(
            os.environ, HOME=str(self.home), GIT_CONFIG_GLOBAL=os.devnull,
            GIT_CONFIG_NOSYSTEM="1", PYTHONDONTWRITEBYTECODE="1",
        )
        self.git(self.source, "init", "-q", "-b", "main")
        (self.source / "tools").mkdir()
        shutil.copy2(SCRIPT, self.source / "tools/setup.py")
        self.baseline = self.source / "docs/copilot/copilot-instructions.md"
        self.baseline.parent.mkdir(parents=True)
        self.baseline.write_text("baseline\n")
        self.skill = self.source / "docs/copilot/skills/devhub-example"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("skill\n")
        (self.skill / "resource.txt").write_text("support\n")
        self.agent = self.source / "docs/copilot/agents/devhub-example.agent.md"
        self.agent.parent.mkdir()
        self.agent.write_text("agent\n")
        self.instruction = self.source / "docs/copilot/instructions/python.instructions.md"
        self.instruction.parent.mkdir()
        self.instruction.write_text("---\napplyTo: '**/*.py'\n---\nPython rules\n")
        self.commit(self.source)
        self.clone = self.workspace / "DevHub"
        self.git(self.workspace, "clone", "-q", str(self.source), str(self.clone))
        self.target = self.workspace / ".github"
        self.state = self.target / ".devhub-setup.json"

    def git(self, repo, *args):
        return subprocess.run(
            ["git", "-C", str(repo), "-c", "user.name=Setup Test",
             "-c", "user.email=test@example.invalid", *args],
            env=self.env, text=True, capture_output=True, check=True,
        ).stdout.strip()

    def commit(self, repo):
        self.git(repo, "add", ".")
        self.git(repo, "commit", "-qm", "test change")
        return self.git(repo, "rev-parse", "HEAD")

    def setup(self, *args, success=True):
        result = subprocess.run(
            [sys.executable, str(self.clone / "tools/setup.py"),
             "--workspace", str(self.workspace), *args],
            env=self.env, text=True, capture_output=True, timeout=15,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_setup_repeat_and_repair_includes_instructions(self):
        self.setup()
        self.assertEqual((self.target / self.baseline.name).read_text(), "baseline\n")
        self.assertEqual((self.target / "skills/devhub-example/resource.txt").read_text(), "support\n")
        self.assertTrue((self.target / "agents" / self.agent.name).is_symlink())
        self.assertEqual((self.target / "instructions" / self.instruction.name).read_text(),
                         self.instruction.read_text())
        self.assertEqual(json.loads(self.state.read_text())["commit"],
                         self.git(self.clone, "rev-parse", "HEAD"))
        (self.target / self.baseline.name).unlink()
        self.setup()
        self.assertTrue((self.target / self.baseline.name).is_symlink())
        self.assertFalse((self.home / ".copilot").exists())
        self.assertEqual(self.git(self.clone, "status", "--porcelain"), "")

    def test_pull_updates_instructions_and_uses_updated_script(self):
        self.setup()
        self.baseline.write_text("new baseline\n")
        script = self.source / "tools/setup.py"
        script.write_text(script.read_text().replace(
            'print(f"DevHub workspace is current at {commit}")',
            'print(f"new script applied {commit}")',
        ))
        commit = self.commit(self.source)
        result = self.setup()
        self.assertIn("new script applied", result.stdout)
        self.assertEqual((self.target / self.baseline.name).read_text(), "new baseline\n")
        self.assertEqual(json.loads(self.state.read_text())["commit"], commit)

    def test_conflict_preserves_existing_file_and_does_not_record_success(self):
        self.target.mkdir()
        local = self.target / self.baseline.name
        local.write_text("personal")
        result = self.setup(success=False)
        self.assertIn("Conflict", result.stderr)
        self.assertEqual(local.read_text(), "personal")
        self.assertFalse(self.state.exists())
        self.assertFalse((self.target / "agents" / self.agent.name).exists())

    def test_unrecorded_link_is_not_claimed(self):
        self.target.mkdir()
        (self.target / self.baseline.name).symlink_to(self.clone / "docs/copilot" / self.baseline.name)
        self.assertIn("Conflict", self.setup(success=False).stderr)

    def test_removed_entries_pruned_and_personal_replacements_preserved(self):
        self.setup()
        replaced = self.target / "agents" / self.agent.name
        replaced.unlink()
        replaced.write_text("mine")
        self.agent.unlink()
        self.instruction.unlink()
        shutil.rmtree(self.skill)
        self.commit(self.source)
        result = self.setup()
        self.assertIn("Preserving personal replacement", result.stderr)
        self.assertEqual(replaced.read_text(), "mine")
        self.assertFalse((self.target / "skills/devhub-example").is_symlink())
        self.assertFalse((self.target / "instructions" / self.instruction.name).is_symlink())

    def test_uninstall_offline_preserves_other_files_and_is_repeatable(self):
        self.setup()
        local = self.target / "skills/local"
        local.mkdir()
        (local / "keep").write_text("mine")
        replaced = self.target / self.baseline.name
        replaced.unlink()
        replaced.write_text("personal")
        self.git(self.clone, "remote", "set-url", "origin", str(self.root / "unavailable"))
        self.setup("--uninstall")
        self.assertFalse(self.state.exists())
        self.assertEqual(replaced.read_text(), "personal")
        self.assertEqual((local / "keep").read_text(), "mine")
        self.assertFalse((self.target / "agents" / self.agent.name).is_symlink())
        self.setup("--uninstall")
        self.assertTrue(self.clone.is_dir())

    def test_pull_failure_keeps_commit_record(self):
        self.setup()
        state = self.state.read_text()
        self.git(self.clone, "remote", "set-url", "origin", str(self.root / "unavailable"))
        self.assertIn("Git operation failed", self.setup(success=False).stderr)
        self.assertEqual(self.state.read_text(), state)
        self.assertEqual((self.target / self.baseline.name).read_text(), "baseline\n")
        self.setup("--no-pull")

    def test_dirty_checkout_is_rejected_without_overwrite(self):
        path = self.clone / "docs/copilot" / self.baseline.name
        path.write_text("local edits")
        self.assertIn("local changes", self.setup(success=False).stderr)
        self.assertEqual(path.read_text(), "local edits")
        self.assertFalse(self.state.exists())

    def test_untracked_files_are_rejected(self):
        (self.clone / "untracked").write_text("mine")
        self.assertIn("local changes", self.setup(success=False).stderr)

    def test_unpublished_commits_are_rejected(self):
        (self.clone / "local").write_text("mine")
        self.commit(self.clone)
        self.assertIn("unpublished commits", self.setup(success=False).stderr)
        self.assertFalse(self.state.exists())

    def test_detached_head_is_rejected(self):
        self.git(self.clone, "checkout", "--detach", "-q")
        self.setup(success=False)
        self.assertFalse(self.state.exists())

    def test_invalid_state_does_not_mutate_links(self):
        self.setup()
        state = json.loads(self.state.read_text())
        state["entries"].append("../outside")
        self.state.write_text(json.dumps(state))
        self.assertIn("Invalid setup state", self.setup("--uninstall", success=False).stderr)
        self.assertTrue((self.target / self.baseline.name).is_symlink())

    def test_wrong_source_in_state_is_rejected(self):
        self.setup()
        state = json.loads(self.state.read_text())
        state["source"] = "/another/clone"
        self.state.write_text(json.dumps(state))
        self.assertIn("different source clone", self.setup(success=False).stderr)

    def test_interrupted_setup_recovers_from_journal(self):
        self.setup()
        state = json.loads(self.state.read_text())
        state["commit"] = None
        self.state.write_text(json.dumps(state))
        (self.target / self.baseline.name).unlink()
        self.setup()
        self.assertIsNotNone(json.loads(self.state.read_text())["commit"])
        self.assertTrue((self.target / self.baseline.name).is_symlink())

    def test_symlinked_destination_directory_is_rejected(self):
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        self.target.mkdir()
        (self.target / "instructions").symlink_to(elsewhere)
        self.assertIn("symlinked destination", self.setup(success=False).stderr)
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_symlinked_root_is_rejected(self):
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        self.target.symlink_to(elsewhere)
        self.assertIn("symlinked destination", self.setup(success=False).stderr)
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_symlinked_state_is_rejected(self):
        self.target.mkdir()
        outside = self.root / "keep"
        outside.write_text("mine")
        self.state.symlink_to(outside)
        self.assertIn("symlinked state", self.setup(success=False).stderr)
        self.assertEqual(outside.read_text(), "mine")

    def test_concurrent_setup_is_rejected(self):
        with (self.clone / ".git/devhub-setup.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertIn("Another DevHub setup", self.setup(success=False).stderr)

    def test_clone_cannot_be_its_own_workspace(self):
        self.workspace = self.clone
        self.assertIn("outside the DevHub clone", self.setup(success=False).stderr)

    def test_missing_baseline_does_not_remove_existing_links(self):
        self.setup()
        self.baseline.unlink()
        self.commit(self.source)
        self.assertIn("Missing baseline", self.setup(success=False).stderr)
        self.assertTrue((self.target / "agents" / self.agent.name).is_symlink())


class RepositoryLayoutTests(unittest.TestCase):
    def test_github_discovery_entries_link_to_docs(self):
        repository = SCRIPT.parents[1]
        canonical = repository / "docs/copilot"
        for entry in ("copilot-instructions.md", "instructions", "agents", "skills"):
            path = repository / ".github" / entry
            self.assertTrue(path.is_symlink(), path)
            self.assertFalse(os.path.isabs(os.readlink(path)), path)
            self.assertEqual(path.resolve(), (canonical / entry).resolve())
        entries = runpy.run_path(str(SCRIPT))["desired_entries"](repository)
        self.assertIn("copilot-instructions.md", entries)
        self.assertTrue(any(e.startswith("skills/devhub-") for e in entries))


if __name__ == "__main__":
    unittest.main()
