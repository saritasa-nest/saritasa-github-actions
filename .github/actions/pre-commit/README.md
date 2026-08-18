# Pre-Commit Composite Action

## Introduction. Pre-Commit

Pre-commit is a framework that runs checks on the code before it gets committed. 

It helps catch issues like formatting errors, security vulnerabilities, and incorrect commit messages before they reach the repository.

All pre-commit checks are defined in a `.pre-commit-config.yaml` file and run automatically on commit/push.

## Description

This GitHub Action installs and configures `pre-commit`, restores cached hook environments, installs repository-specific tools, and runs pre-commit checks.

Pull request runs execute pre-commit checks only against files changed in the PR. 

Pushes to the default branch are used to populate reusable caches that can later be restored by pull requests.

The action also supports checking the latest commit message for a JIRA Task ID and allows specific commit authors to be excluded from this check.

Additional tools required by pre-commit hooks can be defined in the repository `mise.toml` file. 

> In the case that no additional tools are needed, `mise.toml` file doesn't need to be added to the repository root.

## How it works

1. Setup:

- Installs `uv` using `astral-sh/setup-uv`.
- Installs `pre-commit` and `pre-commit-uv` using `uv`.
- Installs additional repository-specific tools from `mise.toml`, if the file exists.
- Restores cached `uv`, `mise`, and pre-commit hook environments where available.

2. Cache pre-commit environments:

Pre-commit hook environments are cached using: runner OS, architecture, python version and `.pre-commit-config.yaml` hash.

Pull requests can restore caches created for the PR or fallback to caches available from the default branch (`main`).

Pushes to the default branch (`main`) **ONLY** populate reusable caches for future pull requests, they skip *running* pre-commit checks. 

Missing pre-commit hook environments are installed via `pre-commit install-hooks` before the cache is saved.

3. Run pre-commit checks:

On pull requests, runs pre-commit only against files changed between the PR base and head commits.

> Binary files are excluded from the changed-files list.

Runs all pre-commit hooks defined in the `.pre-commit-config.yaml` file.

4. Run JIRA commit message check:

Runs the `jira-pre-commit` hook against the latest PR commit message. Can be disabled using `run-jira-pre-commit`.

Authors listed in `ignore-commit-authors` are skipped.

5. Clean up PR caches:

PR-specific caches can be removed when the pull request is closed using the reusable `cleanup-pr-cache.yaml` workflow.

This removes caches scoped to `refs/pull/<PR>/merge`, including `pre-commit`, `uv`, and `mise` caches.

## Usage

Example of how to use this action in a GitHub workflow:

```yaml
---
name: pre-commit
on:
  pull_request:
    types:
      - labeled
      - unlabeled
      - opened
      - reopened
      - synchronize
      - closed
  # Separate PRs can use the same cache only if it's created on default branch (`main`)
  push:
    branches:
      - main
jobs:
  pre-commit:
    # Run job if it's a push event (push to default branch to create reusable cache)
    # Or if PR wasn't created by RenovateBot, not in WIP, and isn't being Closed
    if: |
      github.event_name == 'push' ||
      (
        github.event.action != 'closed' &&
        !contains(github.event.pull_request.labels.*.name, 'renovate') &&
        !contains(github.event.pull_request.labels.*.name, 'wip')
      )
    runs-on: saritasa-rocks-eks
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd  # v6
        with:
          fetch-depth: 0
      - name: Run pre-commit checks
        uses: saritasa-nest/saritasa-github-actions/.github/actions/pre-commit@v6.3
        with:
          python-version: '3.12'
          ignore-commit-authors: |-
            tekton-kustomize
            saritasa-renovatebot
  # Delete all caches created specifically for this PR
  # This includes pre-commit, mise and uv caches scoped to refs/pull/<PR>/merge
  cleanup-pr-cache:
    if: |
      github.event_name == 'pull_request' &&
      github.event.action == 'closed'
    permissions:
      actions: write
    uses: saritasa-nest/saritasa-github-actions/.github/workflows/cleanup-pr-cache.yaml@v6.3
```

## Additional pre-commit tools

If pre-commit hooks require additional CLI tools, define them in `mise.toml` in the repository root:
  - [`mise-action`](https://github.com/jdx/mise-action)

For example:

```toml
[tools]
terraform = "1.12.2"

# Pre-commit tools
terraform-docs = "0.21.0"
trivy = "0.69.3"

# ...
```

The beauty of `mise-action` is that you only need to define tools names and versions, and `mise` itself will resolve what arch your runner uses (i.e. repository can now switch between ARC runners of different architecture without changing `tools-list` to hardcode package names with proper architecture), download it, and export into `GITHUB_PATH`.

> If `mise.toml` does not exist, the mise setup step is skipped. 

## Inputs

| Parameter               | Description                                  | Required | Default          |
| ----------------------- | -------------------------------------------- | -------- | ---------------- |
| `ignore-commit-authors` | List of users to ignore in JIRA commit check | No       | tekton-kustomize |
| `python-version`        | Python version to install                    | No       | 3                |
| `run-jira-pre-commit`   | Whether to run the JIRA commit check         | No       | true             |

### `ignore-commit-authors`

Multiple authors can be provided in a multi-line value:

```yaml
with:
  ignore-commit-authors: |-
    tekton-kustomize
    saritasa-renovatebot
```

If the commit author contains one of the configured values, the JIRA commit message check is skipped.

### `python-version`

The Python version is passed to `astral-sh/setup-uv` and used as `UV_PYTHON`

For example:

```yaml
with:
  python-version: '3.12'
```

By default, `python-version` is `3`. Before switch to `uv`, the default was `3.x`, but that format is unsupported for `setup-uv`.

### `run-jira-pre-commit`

The JIRA commit message check is enabled by default.

It can be disabled when the repository does not use the `jira-pre-commit` hook, with the:

```yaml
with:
  run-jira-pre-commit: 'false'
```

This will result in the JIRA commit message check step to be skipped entirely.

## Caching in the action

The action uses separate caches for `uv`, `mise`, and `pre-commit` hook environments.

The pre-commit cache key has the following format:

`pre-commit-cache-<OS>-<ARCH>-python-<PYTHON_VERSION>-<PRE_COMMIT_CONFIG_HASH>`

This ensures that hook environments are separated when the runner architecture, python version, or `.pre-commit-config.yaml` changes.

GitHub Actions caches are scoped by Git ref, so caches created in **PR A** are not intended to be reused by **PR B/C/D**, only by **PR A** workflows. 

Pushes to the default branch (`main`) **ONLY** populate reusable caches that future PRs can restore. Meaning that they only install hooks and save caches, but skip *running* pre-commit checks.

Read more about GitHub caching: [`Restrictions for accessing cache docs`](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching#restrictions-for-accessing-a-cache)

PR-specific caches can be deleted after the pull request is closed by using the `cleanup-pr-cache.yaml` reusable workflow shown in the usage example:

```yaml
  # Delete all caches created specifically for this PR
  # This includes pre-commit, mise and uv caches scoped to refs/pull/<PR>/merge
  cleanup-pr-cache:
    if: |
      github.event_name == 'pull_request' &&
      github.event.action == 'closed'
    permissions:
      actions: write
    uses: saritasa-nest/saritasa-github-actions/.github/workflows/cleanup-pr-cache.yaml@v6.3
```

That way workflow won't be able to delete different PR caches, or caches from `main` branch. 
