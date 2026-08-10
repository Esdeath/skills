# README Design

## Goal

Create a Chinese-first root `README.md` for public GitHub visitors. A new reader
should understand what the repository contains, install the available skill,
invoke it, and recognize its output within one minute.

## Audience

The primary audience is a Chinese-speaking Codex user discovering the
repository for the first time. Maintainers are a secondary audience, so testing
and publishing details belong after the user workflow.

## Structure

The README follows a use-first order:

1. Repository name and one-sentence purpose.
2. The currently available skill and its core behavior.
3. Prerequisites and installation through `$skill-installer` or a local skill
   directory supported by Codex.
4. Explicit and natural-language invocation examples.
5. Generated files, data principles, and important limitations.
6. Repository layout.
7. Test command and maintainer-only publishing workflow.
8. A link to the official OpenAI skill documentation.

## Content Rules

- Write explanatory prose in concise Chinese; keep commands, paths, filenames,
  and identifiers in English.
- Describe only behavior present in the repository or confirmed by official
  OpenAI documentation.
- Keep the quick-start path near the top and avoid badges, promotional claims,
  screenshots, or sections with no current content.
- Do not invent a license, contribution process, package release, or support
  channel that the repository does not provide.
- Warn that `./deploy.sh` stages every repository change, creates a fixed-message
  commit when needed, and pushes the active branch to `origin`.

## Verification

- Check every referenced path and command against the repository.
- Run the existing unit tests.
- Scan the README for placeholders, broken relative links, contradictions, and
  unsupported claims.
- Give the completed document to a context-free reader agent and revise any
  installation, invocation, or output details it cannot recover reliably.
