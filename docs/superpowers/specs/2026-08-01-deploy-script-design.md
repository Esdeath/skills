# Deploy Script Design

## Goal

Provide a single executable entry point, `./deploy.sh`, that publishes all
current repository changes to the configured GitHub remote with a stable commit
message.

## Structure

- `deploy.sh` is a small shell launcher that resolves the repository root and
  invokes `python3 scripts/deploy.py`.
- `scripts/deploy.py` owns validation, staging, committing, and pushing.
- `tests/test_deploy.py` exercises the Python script against temporary local Git
  repositories and bare remotes.

## Publish Flow

1. Verify that the script is running inside a Git worktree.
2. Verify that an `origin` remote exists.
3. Resolve the current branch and reject detached HEAD state.
4. Stage every change with `git add -A`, including additions, modifications,
   and deletions.
5. If the index contains changes, create a commit with the fixed message
   `chore: update project`.
6. If the index contains no changes, print a short message and skip the commit.
7. Push the current branch with `git push -u origin <branch>`.

## Safety And Errors

The script stops immediately when a Git command fails and returns a non-zero
exit status. It does not pull, switch branches, rewrite commits, or force push.
Git output remains visible so authentication, remote, and merge errors are
actionable.

## Testing

Tests create isolated temporary repositories and local bare remotes. They cover:

- publishing staged and unstaged additions, modifications, and deletions;
- using the fixed commit message;
- pushing the active branch and configuring its upstream;
- skipping commit creation when the worktree has no changes;
- clear failure for a missing remote or detached HEAD.
