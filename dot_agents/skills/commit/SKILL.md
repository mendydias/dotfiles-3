---
name: commit
description: Use when the user explicitly asks to commit changes or draft a commit message. Creates a Conventional Commit after checking repository rules and the exact diff.
---

# Sentry Commit Messages

## Before Committing

```bash
git branch --show-current
```

Do not switch branches or create a branch unless the user explicitly asks.

Commit one coherent, independently reviewable change at a time.

## Message Rules

Use:

```text
<type>(<scope>): <subject>

<optional body>

<optional footer>
```

- Scope is optional. Add `!` before `:` for a breaking change.
- Write the subject in imperative, present tense; capitalize it, omit the
  trailing period, and keep it at 70 characters or fewer.
- Keep every line under 100 characters.
- Use the body only when useful. Explain what changed and why, including
  previous behavior or motivation when it helps.
- Never include customer or organization names, user emails, support ticket
  contents, secrets, or PII. Describe the technical symptom instead.

Allowed types: `feat`, `fix`, `ref`, `perf`, `docs`, `test`, `build`,
`ci`, `chore`, `style`, `meta`, `license`, and `revert`.

Use `ref` for refactoring without behavior changes, `style` for formatting
without logic changes, and `meta` for repository metadata.

## Footers

- `Fixes <issue>` closes an issue when merged.
- `Refs <issue>` links an issue without closing it.
- For breaking changes, add `BREAKING CHANGE: <impact>`.

## Creating the Commit

Preserve the user's staged and unstaged changes. Never stage all files, unstage
existing work, or commit unrelated changes. If the intended commit scope is not
already staged and unambiguous, ask which paths to include and stage only those.
Do not push, open a pull request, or amend an existing commit unless asked.

Use separate `-m` arguments for paragraphs and footers. Never put literal
`\n` sequences in a commit message or open an interactive editor.

```bash
git commit -m "fix(api): Handle null response in user endpoint" \
  -m "Return 404 when the user API finds a deleted account." \
  -m "Fixes SENTRY-5678"
```
