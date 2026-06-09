---
name: ship-and-babysit
description: Commit local changes, push the branch, open or reuse a PR, then babysit CI and code review feedback until the PR is green and clean. Use when the user wants an end-to-end ship flow, not just implementation.
model: inherit
---

# Ship And Babysit

You are running an end-to-end ship-and-babysit flow for this repository. Follow these phases in order. Be concise in user-facing text.

## Repo Facts

- Upstream: `origin` (user's fork)
- PRs target `main`
- Push branches to `origin`
- PRs are opened with `--head <fork-owner>:<branch>` against `main`
- PR template: `.github/PULL_REQUEST_TEMPLATE.md` (if exists)

Resolve the fork owner once at the start and reuse it:

```bash
FORK_OWNER=$(git remote get-url origin | sed -E 's#.*[:/]([^/]+)/[^/]+(\.git)?$#\1#')
```

## Phase 1 — Commit

1. Inspect `git status`, staged and unstaged diffs, and recent commit messages.
2. If nothing changed and the branch is already pushed and already has a PR, skip to Phase 4.
3. If there are local changes, stage only the relevant files and create a conventional commit (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`).
4. Do not bypass commit hooks for your own changes.

## Phase 2 — Push

1. Confirm the current branch is not `main`.
2. Push to `origin`, using `-u` if upstream tracking is missing.
3. If the pre-push hook fails on unrelated pre-existing breakage, push with `--no-verify` and record that explicitly in the PR body. If the hook fails on your own changes, fix the problem and push again.

## Phase 3 — Open PR

1. Check whether a PR already exists for this branch:

```bash
gh pr list --head <fork-owner>:<branch> --state open --json number,url
```

2. If no PR exists, write a title and a body. Inspect `git log main..HEAD` and `git diff main...HEAD` first.
   - Every checklist item must be checked; use `- [x] N/A: <reason>` when an item does not apply.
3. Create the PR against `main`.
4. Capture the PR number and URL for the babysit loop.

## Phase 4 — Babysit Loop

Repeat until the PR is clean:

1. Check CI:

```bash
gh pr checks <PR#> --json name,state,link,description
```

2. If an Actions-backed check fails, fetch failed logs with `gh run view <run-id> --log-failed`, fix the issue, commit, and push.
3. Check review comments:

```bash
gh api repos/<owner>/<repo>/pulls/<PR#>/comments --paginate
gh api repos/<owner>/<repo>/issues/<PR#>/comments --paginate
```

4. Apply correct in-scope suggestions. If a suggestion is wrong or out of scope, reply in-thread with a short dismissal reason before resolving it.
5. Resolve addressed review threads through the GitHub GraphQL API.
6. Exit only when required checks are successful and no unresolved review threads remain.

## Guardrails

- Never push to `main` directly.
- Never force-push to `main`.
- Never resolve a review thread without either fixing the issue or replying with a reasoned dismissal.
- Do not merge the PR. Stop at green CI plus clean review state.