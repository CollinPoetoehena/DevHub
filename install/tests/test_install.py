"""Isolated integration tests; no network access or real home changes."""

import os
from pathlib import Path
import fcntl
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


INSTALLER = Path(__file__).resolve().parents[1] / "install.py"


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="devhub-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.home = self.root / "home with spaces"
        self.home.mkdir()
        self.data = self.home / "data/devhub"
        self.source = self.root / "source"
        (self.source / "install").mkdir(parents=True)
        shutil.copy2(INSTALLER, self.source / "install/install.py")
        self.skill = self.source / ".github/skills/devhub-example"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("skill\n")
        (self.skill / "resource.txt").write_text("support\n")
        self.agent = self.source / ".github/agents/devhub-example.agent.md"
        self.agent.parent.mkdir(parents=True)
        self.agent.write_text("agent\n")
        self.environment = dict(
            os.environ, HOME=str(self.home), XDG_DATA_HOME=str(self.home / "data"),
            GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
            PYTHONDONTWRITEBYTECODE="1",
        )
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Installer Test")
        self.git("config", "user.email", "test@example.invalid")
        self.commit()

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.source), *args], env=self.environment,
            check=True, text=True, capture_output=True,
        ).stdout.strip()

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "test revision")
        return self.git("rev-parse", "HEAD")

    def run_installer(self, *args, installed=False, success=True):
        script = self.data / "install.py" if installed else INSTALLER
        result = subprocess.run(
            [sys.executable, str(script), "--source", self.source.as_uri(), *args],
            env=self.environment, text=True, capture_output=True, timeout=30,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def destination(self, name="devhub-example"):
        return self.home / ".copilot/skills" / name

    def test_install_repeat_repair_and_supporting_resources(self):
        self.run_installer()
        commit = (self.data / "installed-commit").read_text().strip()
        self.assertEqual(commit, self.git("rev-parse", "HEAD"))
        self.assertEqual((self.destination() / "resource.txt").read_text(), "support\n")
        self.assertTrue((self.home / ".copilot/agents" / self.agent.name).is_symlink())
        self.run_installer(installed=True)
        self.assertEqual(len(list((self.data / "releases").iterdir())), 1)
        self.destination().unlink()
        self.run_installer()
        self.assertTrue(self.destination().is_symlink())
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_conflicts_fail_without_success_state(self):
        self.destination().mkdir(parents=True)
        personal = self.destination() / "personal"
        personal.write_text("keep")
        result = self.run_installer(success=False)
        self.assertIn("Conflict", result.stderr)
        self.assertEqual(personal.read_text(), "keep")
        self.assertFalse((self.data / "installed-commit").exists())

    def test_update_removes_owned_links_preserves_replacements(self):
        obsolete = self.agent.with_name("devhub-obsolete.agent.md")
        obsolete.write_text("obsolete")
        self.commit()
        self.run_installer()
        old_commit = (self.data / "installed-commit").read_text()
        replacement = self.home / ".copilot/agents" / self.agent.name
        replacement.unlink()
        replacement.write_text("personal")
        self.agent.unlink()
        obsolete.unlink()
        renamed = self.skill.with_name("devhub-renamed")
        self.skill.rename(renamed)
        (renamed / "SKILL.md").write_text("updated")
        self.commit()
        self.run_installer(installed=True)
        self.assertFalse(self.destination().is_symlink())
        self.assertFalse((replacement.parent / obsolete.name).is_symlink())
        self.assertEqual(replacement.read_text(), "personal")
        self.assertEqual((self.destination("devhub-renamed") / "SKILL.md").read_text(), "updated")
        self.assertNotEqual((self.data / "installed-commit").read_text(), old_commit)

    def test_failed_download_preserves_installation(self):
        self.run_installer()
        state = (self.data / "installed-commit").read_text()
        self.run_installer("--source", str(self.root / "missing"), success=False)
        self.assertEqual((self.data / "installed-commit").read_text(), state)
        self.assertEqual((self.destination() / "SKILL.md").read_text(), "skill\n")

    def test_uninstall_offline_repeated_and_reinstall(self):
        self.run_installer()
        old_commit = (self.data / "installed-commit").read_text().strip()
        personal = self.home / ".copilot/skills/personal"
        personal.mkdir()
        (personal / "file").write_text("keep")
        cache = self.data / "releases/personal-cache"
        cache.mkdir()
        self.destination().unlink()
        self.destination().mkdir()
        (self.destination() / "personal").write_text("replacement")
        self.run_installer("--uninstall", "--source", "/unavailable", installed=True)
        self.assertEqual((self.destination() / "personal").read_text(), "replacement")
        self.assertEqual((personal / "file").read_text(), "keep")
        self.assertTrue(cache.is_dir())
        self.assertFalse((self.data / "releases" / old_commit).exists())
        self.assertFalse((self.data / "installed-commit").exists())
        self.assertFalse((self.data / "install.py").exists())
        self.assertFalse((self.data / "current").is_symlink())
        self.run_installer("--uninstall")
        shutil.rmtree(self.destination())
        self.run_installer()
        self.assertTrue(self.destination().is_symlink())

    def test_invalid_manifest_aborts_uninstall_before_mutation(self):
        self.run_installer()
        with (self.data / "ai-links").open("a") as manifest:
            manifest.write("../outside\n")
        result = self.run_installer("--uninstall", installed=True, success=False)
        self.assertIn("Invalid ownership manifest", result.stderr)
        self.assertTrue(self.destination().is_symlink())
        self.assertTrue((self.data / "installed-commit").exists())

    def test_empty_release_and_unrecognized_cache(self):
        self.run_installer()
        shutil.rmtree(self.source / ".github")
        self.commit()
        self.run_installer()
        self.assertFalse(self.destination().is_symlink())
        self.assertEqual((self.data / "ai-links").read_text(), "")
        commit = (self.data / "installed-commit").read_text().strip()
        (self.data / "releases" / commit / ".devhub-release").unlink()
        self.run_installer(success=False)
        self.run_installer("--uninstall")
        self.assertTrue((self.data / "releases" / commit).exists())

    def test_downloaded_installer_functions_are_used(self):
        script = self.source / "install/install.py"
        text = script.read_text().replace(
            "    install_ai_customizations(home, data, release)",
            '    print("downloaded component version")\n'
            "    install_ai_customizations(home, data, release)",
        )
        script.write_text(text)
        self.commit()
        self.assertIn("downloaded component version", self.run_installer().stdout)

    def test_relative_data_directory_is_rejected(self):
        self.environment["XDG_DATA_HOME"] = "relative"
        result = self.run_installer(success=False)
        self.assertIn("absolute paths", result.stderr)

    def test_lock_contention_times_out_without_unlocking_other_process(self):
        functions = runpy.run_path(str(INSTALLER))
        self.data.mkdir(parents=True)
        with (self.data / "install.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with patch("time.monotonic", side_effect=[0, 31]):
                with self.assertRaisesRegex(TimeoutError, "Another DevHub"):
                    with functions["installation_lock"](self.data):
                        self.fail("Acquired an already held lock")

    def test_interrupted_link_creation_can_be_repaired_and_uninstalled(self):
        self.run_installer()
        self.destination().unlink()
        functions = runpy.run_path(str(INSTALLER))
        commit = (self.data / "installed-commit").read_text().strip()
        release = self.data / "releases" / commit
        original = Path.symlink_to

        def fail_skill_link(target, *args, **kwargs):
            if target == self.destination():
                raise OSError("simulated interruption")
            return original(target, *args, **kwargs)

        with patch.object(Path, "symlink_to", fail_skill_link):
            with self.assertRaisesRegex(OSError, "simulated interruption"):
                functions["install_ai_customizations"](self.home, self.data, release)
        self.assertIn("skills/devhub-example", (self.data / "ai-links").read_text())
        self.run_installer()
        self.assertTrue(self.destination().is_symlink())
        self.run_installer("--uninstall", installed=True)
        self.assertFalse(self.destination().is_symlink())


if __name__ == "__main__":
    unittest.main()
