# Releasing SOOPEX

This document describes the release process for the `soopex` package. Each
release is driven by a git tag — the `release.yml` workflow picks up the tag,
builds wheels/sdists, and publishes via PyPI trusted publishing.

## One-time setup

The first release requires the following manual setup (author only).

### 1. Trusted publishing on TestPyPI

1. Create an account on <https://test.pypi.org>.
2. At <https://test.pypi.org/manage/account/publishing/>, add a
   **pending publisher** with:
   - PyPI Project Name: `soopex`
   - Owner: `h-shiono`
   - Repository name: `soopex`
   - Workflow name: `release.yml`
   - Environment name: `testpypi`

### 2. Trusted publishing on PyPI

Same flow at <https://pypi.org/manage/account/publishing/> with:
- Environment name: `pypi`

### 3. GitHub environments

In the GitHub repo settings → **Environments**, create two environments:

- `testpypi` — no protection rules needed.
- `pypi` — add **Required reviewers** (yourself) so a human approval is
  required before each PyPI publish.

## Cutting a release

1. Update `CHANGELOG.md`: move entries from `[Unreleased]` into the new
   version section, add the release date.
2. Bump `src/soopex/_version.py` to the target version (e.g. `"0.1.0a2"`).
3. Commit the changes:
   ```bash
   git add CHANGELOG.md src/soopex/_version.py
   git commit -m "release: 0.1.0a2"
   ```
4. Tag and push:
   ```bash
   git tag v0.1.0a2
   git push origin main --tags
   ```
5. The `release.yml` workflow runs automatically. It always publishes to
   TestPyPI; it publishes to PyPI **only** for non-prerelease tags (no
   `a` / `b` / `rc` suffix in the version).

## Tag conventions

| Tag          | Action                      | Notes                       |
|--------------|-----------------------------|-----------------------------|
| `v0.1.0a1`   | TestPyPI only               | Alpha (prerelease)          |
| `v0.1.0b1`   | TestPyPI only               | Beta (prerelease)           |
| `v0.1.0rc1`  | TestPyPI only               | Release candidate           |
| `v0.1.0`     | TestPyPI **and** PyPI       | Production release          |

The `pypi` job is gated by the `pypi` environment, so a required reviewer
has to approve the PyPI publish step from the Actions UI.

## Local dry-run

Before cutting a tag, verify the build locally:

```bash
uv build
ls dist/
# soopex-0.1.0a2.tar.gz
# soopex-0.1.0a2-py3-none-any.whl
```

## Reserving the name on TestPyPI (first release only)

To defensively reserve the `soopex` name before the first GitHub push,
upload a throwaway version directly:

```bash
uv build
uv publish --publish-url https://test.pypi.org/legacy/ --token <testpypi-token>
```

(Requires a classic TestPyPI API token; can be revoked after trusted
publishing is configured.)
