# SentinelDesk App Security Demo (Milestone 6)

A minimal, intentionally vulnerable Flask app used to validate an automated
security gate in a pull request pipeline. Nothing here should be reused —
the vulnerabilities are deliberate.

## What's wired up

- **SAST — CodeQL** (`.github/workflows/codeql.yml`): scans Python source on
  every push and pull request against `main`. `app.py`'s `/documents`
  endpoint contains a deliberate SQL injection (string-formatted query
  instead of a parameterized one) that CodeQL's default `py/sql-injection`
  query should flag.
- **SCA — Dependabot** (`.github/dependabot.yml`): scans `requirements.txt`
  daily for known vulnerabilities in pinned dependency versions and opens
  pull requests to bump them. `requirements.txt` deliberately pins old
  versions of Flask and PyYAML — Dependabot's own advisory lookup is what
  should surface the specific CVEs, rather than us asserting them ourselves.

## Exercise sequence

1. Push this repo to GitHub as-is on `main` (findings won't show until
   scanning runs at least once).
2. Confirm Dependabot alerts appear under the repo's **Security** tab.
3. Create a branch, make a trivial change to `app.py` (e.g. add a comment),
   and open a pull request back to `main`. Confirm the CodeQL check runs on
   the PR and either flags the injection or blocks/warns depending on how
   branch protection is configured.
4. Compare `list_documents_vulnerable` against `list_documents_safe` in
   `app.py` to see the fix pattern CodeQL expects.
