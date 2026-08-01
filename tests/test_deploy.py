import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "deploy.py"
LAUNCHER = Path(__file__).resolve().parents[1] / "deploy.sh"


def git(directory: Path, *args: str, capture: bool = True) -> str:
    result = subprocess.run(
        ["git", *args], cwd=directory, text=True, capture_output=capture, check=True
    )
    return result.stdout.strip() if result.stdout else ""


def git_dir(directory: Path, *args: str) -> str:
    return git(directory, f"--git-dir={directory}", *args)


def git_dir_result(directory: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", f"--git-dir={directory}", *args], text=True, capture_output=True
    )


class DeployScriptTests(unittest.TestCase):
    def make_repository(self, with_remote: bool = True) -> tuple[Path, Path]:
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        root = Path(temporary_directory.name)
        repo = root / "repo"
        remote = root / "origin.git"

        git(root, "init", "--bare", "--initial-branch=main", str(remote))
        git(root, "init", "--initial-branch=main", str(repo))
        git(repo, "config", "user.name", "Deploy Test")
        git(repo, "config", "user.email", "deploy-test@example.com")
        (repo / "scripts").mkdir()
        shutil.copy(LAUNCHER, repo / "deploy.sh")
        shutil.copy(SCRIPT, repo / "scripts" / "deploy.py")
        (repo / "tracked.txt").write_text("original\n", encoding="utf-8")
        (repo / "deleted.txt").write_text("delete me\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-m", "Initial commit")
        if with_remote:
            git(repo, "remote", "add", "origin", str(remote))
            git(repo, "push", "-u", "origin", "main")
        return repo, remote

    def run_deploy(self, repo: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT)], cwd=repo, text=True, capture_output=True
        )

    def test_publishes_all_changes_with_fixed_commit_message(self):
        repo, remote = self.make_repository()
        (repo / "tracked.txt").write_text("updated\n", encoding="utf-8")
        (repo / "deleted.txt").unlink()
        (repo / "new.txt").write_text("new\n", encoding="utf-8")

        result = self.run_deploy(repo)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(git(repo, "log", "-1", "--format=%s"), "chore: update project")
        self.assertEqual(git(repo, "status", "--porcelain"), "")
        self.assertEqual(git_dir(remote, "show", "main:tracked.txt"), "updated")
        self.assertEqual(git_dir(remote, "show", "main:new.txt"), "new")
        deleted = git_dir_result(remote, "cat-file", "-e", "main:deleted.txt")
        self.assertNotEqual(deleted.returncode, 0)
        self.assertEqual(git(repo, "rev-parse", "--abbrev-ref", "@{upstream}"), "origin/main")

    def test_skips_commit_when_there_are_no_changes_and_still_pushes(self):
        repo, _ = self.make_repository()
        before = git(repo, "rev-list", "--count", "HEAD")

        result = self.run_deploy(repo)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No changes to commit.", result.stdout)
        self.assertEqual(git(repo, "rev-list", "--count", "HEAD"), before)

    def test_fails_clearly_when_origin_is_missing(self):
        repo = self.make_repository(with_remote=False)[0]

        result = self.run_deploy(repo)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("origin remote is not configured", result.stderr)

    def test_fails_clearly_in_detached_head_state(self):
        repo, _ = self.make_repository()
        git(repo, "checkout", "--detach", capture=False)

        result = self.run_deploy(repo)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("detached HEAD", result.stderr)

    def test_launcher_publishes_from_outside_repository(self):
        repo, _ = self.make_repository()
        (repo / "new.txt").write_text("via launcher\n", encoding="utf-8")
        result = subprocess.run(
            [str(repo / "deploy.sh")],
            cwd=repo.parent,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(git(repo, "log", "-1", "--format=%s"), "chore: update project")
