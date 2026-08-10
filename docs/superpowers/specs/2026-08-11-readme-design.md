# Bilingual README Design

## Goal

Create two root documents for public GitHub visitors: a Chinese-first
`README.md` and an English `README.en.md`. A new reader should understand what
the repository contains, install the available skill, invoke it, and recognize
its output within one minute.

## Audience

The primary audience is a Chinese- or English-speaking Codex user discovering
the repository for the first time. Maintainers are a secondary audience, so
testing and publishing details belong after the user workflow.

## Structure

Both documents follow the same use-first order:

1. A link to the other language version.
2. Repository name and one-sentence purpose.
3. The currently available skill and its core behavior.
4. Prerequisites and installation through `$skill-installer` or a local skill
   directory supported by Codex.
5. Explicit and natural-language invocation examples.
6. Generated files, data principles, and important limitations.
7. Repository layout.
8. Test command and maintainer-only publishing workflow.
9. A link to the official OpenAI skill documentation.

## Content Rules

- Write `README.md` in concise Chinese and `README.en.md` in natural English;
  keep commands, paths, filenames, and identifiers identical in both.
- Keep the two documents structurally and factually equivalent without forcing
  sentence-by-sentence literal translation.
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
- Compare both documents for matching sections, commands, links, warnings, and
  behavioral claims.
- Run the existing unit tests.
- Scan both READMEs for placeholders, broken relative links, contradictions, and
  unsupported claims.
- Give the completed documents to a context-free reader agent and revise any
  installation, invocation, or output details it cannot recover reliably.
