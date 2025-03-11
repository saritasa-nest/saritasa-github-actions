# Pre-Commit Composite Action

## Introduction. Pre-Commit

Pre-commit is a framework that runs checks on the code before it gets committed. It helps catch issues like formatting errors, security vulnerabilities, and incorrect commit messages before they reach the repository. 
All pre-commit checks are defined in a `.pre-commit-config.yaml` file and run automatically on commit/push.  

## Description  

This GitHub Action runs pre-commit checks to help maintain code quality by blocking merges and pushes to `develop` and `main` branches.
If the commit/push was made without running local pre-commit checks (e.g. using `--no-verify`), pre-commit checks will fail and merging will be blocked.

## How it works

1. Setup:
  - Installs Python, Node.js, and Terraform.
  - Installs needed pre-commit tools.
  - Caches tools to speed up future runs.
2. Run pre-Commit checks:
  - Runs all pre-commit hooks from .pre-commit-config.yaml.
  - Checks if commit messages include a JIRA task ID.
3. Block bad commits:
  - Stops merging into develop and main if checks fail.

## Usage  

Example of how to use this action in a GitHub workflow:  

```yaml
jobs:
  pre-commit:
    runs-on: saritasa-rocks-eks
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run pre-commit checks
        uses: saritasa-nest/saritasa-github-actions/.github/actions/pre-commit@v3.4
        with:
          ignore-commit-authors: autocommit-bot
          node-version: '20'
          python-version: '3.13'
          tools-list: |
            tool_name_1=https://tool_url_1.tar.gz
            tool_name_2=https://tool_url_2.tar.gz
```

## Inputs

| Parameter | Description | Required | Default |
| --- | --- | --- | --- |
| `ignore-commit-authors` | List of users to ignore in JIRA commit check | No | tekton-kustomize |
| `node-version` | Node.js version to install | No | 20 |
| `python-version` | Python version to install | No | 3.x |
| `tools-list` | List of tools to download | Yes | "" |

## Example repository

This composite action is used in the `saritasa-terraform-modules` repository (https://github.com/saritasa-nest/saritasa-terraform-modules/blob/main/.github/workflows/pre-commit.yaml)
