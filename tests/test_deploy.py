import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "deploy.py"


def git(directory: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=directory, text=True, capture_output=True, check=True
    )
    return result.stdout.strip()


def git_dir(directory: Path, *args: str) -> str:
    return git(directory, f"--git-dir={directory}", *args)


def git_dir_result(directory: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", f"--git-dir={directory}", *args], text=True, capture_output=True
    )


class DeployScriptTests(unittest.TestCase):
    def make_repository(self) -> tuple[Path, Path]:
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        root = Path(temporary_directory.name)
        repo = root / "repo"
        remote = root / "origin.git"

        git(root, "init", "--bare", "--initial-branch=main", str(remote))
        git(root, "init", "--initial-branch=main", str(repo))
        git(repo, "config", "user.name", "Deploy Test")
        git(repo, "config", "user.email", "deploy-test@example.com")
        (repo / "tracked.txt").write_text("original\n", encoding="utf-8")
        (repo / "deleted.txt").write_text("delete me\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-m", "Initial commit")
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
