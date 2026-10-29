"""Test legacy setup rejection and safe offline cleanup using local repositories."""

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
from unittest import mock


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

    def historical_setup(self):
        """Seed the version-1 journal and links produced by the retired installer."""
        self.target.mkdir()
        entries = [
            "copilot-instructions.md", "skills/devhub-example",
            "agents/devhub-example.agent.md", "instructions/python.instructions.md",
        ]
        for entry in entries:
            path = self.target / entry
            path.parent.mkdir(exist_ok=True)
            path.symlink_to(self.clone / "docs/copilot" / entry,
                            target_is_directory=entry.startswith("skills/"))
        self.state.write_text(json.dumps({
            "version": 1, "source": str(self.clone), "entries": entries,
            "commit": self.git(self.clone, "rev-parse", "HEAD"),
        }))
        return entries

    def test_install_and_no_pull_rejected_before_pull_or_workspace_mutation(self):
        before = self.git(self.clone, "rev-parse", "HEAD")
        self.baseline.write_text("new baseline\n")
        self.commit(self.source)
        for options in ((), ("--no-pull",)):
            with self.subTest(options=options):
                result = self.setup(*options, success=False)
                self.assertIn("install/update is retired", result.stderr)
                self.assertIn("packages/apm/common/README.md", result.stderr)
                self.assertIn("--uninstall", result.stderr)
                self.assertFalse(self.target.exists())
                self.assertFalse((self.clone / ".git/devhub-setup.lock").exists())
                self.assertEqual(self.git(self.clone, "rev-parse", "HEAD"), before)
                self.assertEqual(self.git(self.clone, "status", "--porcelain"), "")

    def test_update_rejection_preserves_historical_state_and_links(self):
        entries = self.historical_setup()
        state = self.state.read_bytes()
        shutil.rmtree(self.clone / "docs/copilot")
        for options in ((), ("--no-pull",)):
            with self.subTest(options=options):
                self.assertIn("APM", self.setup(*options, success=False).stderr)
                self.assertEqual(self.state.read_bytes(), state)
                for entry in entries:
                    self.assertEqual(os.readlink(self.target / entry),
                                     str(self.clone / "docs/copilot" / entry))
                self.assertFalse((self.target / ".devhub-setup.lock").exists())

    def test_install_rejected_without_git_or_destination_helper_calls(self):
        main = runpy.run_path(str(SCRIPT))["main"]
        with mock.patch.object(sys, "argv", [str(SCRIPT), "--workspace", str(self.workspace)]):
            with mock.patch.dict(main.__globals__, git=mock.Mock(), directory=mock.Mock()):
                self.assertEqual(main(), 1)
                main.__globals__["git"].assert_not_called()
                main.__globals__["directory"].assert_not_called()

    def test_uninstall_offline_preserves_other_files_and_is_repeatable(self):
        self.historical_setup()
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

    def test_uninstall_removes_recorded_broken_links_without_old_sources(self):
        entries = self.historical_setup()
        shutil.rmtree(self.clone / "docs/copilot")
        self.git(self.clone, "checkout", "--detach", "-q")
        self.git(self.clone, "remote", "set-url", "origin", str(self.root / "unavailable"))
        self.setup("--uninstall", "--no-pull")
        for entry in entries:
            self.assertFalse((self.target / entry).is_symlink(), entry)
        self.assertFalse(self.state.exists())
        self.assertFalse((self.clone / "docs/copilot").exists())

    def test_uninstall_preserves_unrecorded_and_retargeted_links(self):
        self.historical_setup()
        unrecorded = self.target / "agents/devhub-personal.agent.md"
        unrecorded.symlink_to(self.clone / "docs/copilot/agents/devhub-personal.agent.md")
        replaced = self.target / "instructions" / self.instruction.name
        replaced.unlink()
        replaced.symlink_to(self.root / "personal-instructions.md")
        result = self.setup("--uninstall")
        self.assertIn("Preserving personal replacement", result.stderr)
        self.assertEqual(os.readlink(unrecorded),
                         str(self.clone / "docs/copilot/agents/devhub-personal.agent.md"))
        self.assertEqual(os.readlink(replaced), str(self.root / "personal-instructions.md"))

    def test_uninstall_without_setup_does_not_create_workspace_directory(self):
        self.setup("--uninstall")
        self.assertFalse(self.target.exists())

    def test_invalid_state_does_not_mutate_links(self):
        self.historical_setup()
        state = json.loads(self.state.read_text())
        state["entries"].append("../outside")
        self.state.write_text(json.dumps(state))
        self.assertIn("Invalid setup state", self.setup("--uninstall", success=False).stderr)
        self.assertTrue((self.target / self.baseline.name).is_symlink())

    def test_wrong_source_in_state_is_rejected(self):
        self.historical_setup()
        state = json.loads(self.state.read_text())
        state["source"] = "/another/clone"
        self.state.write_text(json.dumps(state))
        self.assertIn("different source clone", self.setup("--uninstall", success=False).stderr)
        self.assertTrue((self.target / self.baseline.name).is_symlink())

    def test_uninstall_accepts_interrupted_install_journal(self):
        entries = self.historical_setup()
        state = json.loads(self.state.read_text())
        state["commit"] = None
        self.state.write_text(json.dumps(state))
        (self.target / self.baseline.name).unlink()
        self.setup("--uninstall")
        self.assertFalse(self.state.exists())
        for entry in entries:
            self.assertFalse((self.target / entry).is_symlink())

    def test_symlinked_destination_directory_is_rejected(self):
        self.historical_setup()
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        (self.target / "instructions" / self.instruction.name).unlink()
        (self.target / "instructions").rmdir()
        (self.target / "instructions").symlink_to(elsewhere)
        self.assertIn("symlinked destination", self.setup("--uninstall", success=False).stderr)
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_symlinked_root_is_rejected(self):
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        self.target.symlink_to(elsewhere)
        self.assertIn("symlinked destination", self.setup("--uninstall", success=False).stderr)
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_symlinked_state_is_rejected(self):
        self.target.mkdir()
        outside = self.root / "keep"
        outside.write_text("mine")
        self.state.symlink_to(outside)
        self.assertIn("symlinked state", self.setup("--uninstall", success=False).stderr)
        self.assertEqual(outside.read_text(), "mine")

    def test_concurrent_setup_is_rejected(self):
        self.historical_setup()
        with (self.clone / ".git/devhub-setup.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertIn("Another DevHub setup", self.setup("--uninstall", success=False).stderr)

    def test_clone_cannot_be_its_own_workspace(self):
        self.workspace = self.clone
        self.assertIn("outside the DevHub clone", self.setup("--uninstall", success=False).stderr)

    def test_uninstall_without_state_preserves_existing_links(self):
        self.historical_setup()
        self.state.unlink()
        self.setup("--uninstall")
        self.assertTrue((self.target / self.baseline.name).is_symlink())


class RepositoryLayoutTests(unittest.TestCase):
    def test_retired_source_is_not_required_for_cleanup(self):
        repository = SCRIPT.parents[1]
        module = runpy.run_path(str(SCRIPT))
        self.assertEqual(module["CUSTOMIZATIONS"], Path("docs/copilot"))
        self.assertTrue((repository / "packages/apm/common/apm.yml").is_file())
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            with self.assertRaisesRegex(ValueError, "APM"):
                module["synchronize"](repository, workspace, False)
            self.assertEqual(list(workspace.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
