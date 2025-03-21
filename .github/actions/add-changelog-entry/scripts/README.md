# Purpose
Automatically generate a CHANGELOG.md entry whenever a new PR is created.
Action can be run in an open PR and will commit in HEAD branch of PR
It can also be configured in base branch mode, where it will run after the PR is merged and the commit will be made directly in the BASE branch (main/develop).

### Example Workflow for `run_in_base_branch: true`

```yaml
name: changelog-update

on:
  pull_request:
    types: [closed]
  # Allows to run this workflow manually from the Actions tab
  workflow_dispatch:

permissions:
    # Allows the action to push the updated CHANGELOG file
    contents: write

jobs:
  check-changelog:
    # Only run job if PR was created by RenovateBot (has the renovate label)
    if: github.event.pull_request.merged && contains(github.event.pull_request.labels.*.name, 'renovate')
    runs-on: saritasa-rocks-eks
    steps:
      - uses: actions/checkout@v4
      - name: Add entry to CHANGELOG
        uses: saritasa-nest/saritasa-github-actions/.github/actions/add-changelog-entry@main
        with:
          environment: prod
          changelog_path: CHANGELOG.md
          run_in_base_branch: 'true'
          # Github App: saritasa-changelog: https://github.com/organizations/saritasa-nest/settings/apps/saritasa-changelog
          # https://keys.saritasa.cloud/cred/detail/H2atFvKrn59dnNW5kk68ko/
          github_app_id: ${{ vars.changelog_app_id }}
          github_app_private_key: ${{ secrets.changelog_app_private_key }}
          github_app_name: saritasa-changelog
```

### Example Workflow for `run_in_base_branch: false`

```yaml
name: changelog-update

on:
  pull_request:
    # synchronize: so action will trigger on subsequent commits pushed to the PR
    types: [opened, synchronize, reopened]
  # Allows to run this workflow manually from the Actions tab
  workflow_dispatch:

permissions:
    # Allows the action to push the updated CHANGELOG file
    contents: write

jobs:
  check-changelog:
    # Only run job if PR was created by RenovateBot (has the renovate label)
    if: contains(github.event.pull_request.labels.*.name, 'renovate')
    runs-on: saritasa-rocks-eks
    steps:
      - uses: actions/checkout@v4
      - name: Add entry to CHANGELOG
        uses: saritasa-nest/saritasa-github-actions/.github/actions/add-changelog-entry@main
        with:
          environment: prod # this is the default of the action. Added here as an example
          changelog_path: CHANGELOG.md # this is the default of the action. Added here as an example
          run_in_base_branch: false
```

### Inputs

- `environment`: (defaults to `dev`) specify which sub-title should have each entry in the PRs.
- `changelog_path`: (defaults to {{ $.github.basedir }}/CHANGELOG.md)
- `changelog_create_if_missing`: (defaults to true) Create a new CHANGELOG.md file if it does not exist.
- `run_in_base_branch`: (defaults to `false`) Set to `true` to commit to the base branch after PR is merged, `false` to commit directly to the open PR.
- `github_app_id`: (Required if `run_in_base_branch` is `true`) The GitHub App ID.
- `github_app_private_key`: (Required if `run_in_base_branch` is `true`) The GitHub App private key.
- `github_app_name`: (defaults to `saritasa-renovatebot`) The GitHub App name. If using changelog app, specify it as `saritasa-changelog`.

### Notes

- The action will not duplicate dates in the `CHANGELOG.md` file.
- If the PR number already exists in the changelog, the action will exit without making changes.
- The commit author will be `saritasa-renovatebot` when `run_in_base_branch` is `false`.
- When running in `run_in_base_branch: true` mode:
  - Ensure the `Do not allow bypassing the above settings config` option is disabled to allow Admins to bypass branch protections.
  - Ensure that `Mergeable: Сhecking for the presence of the CHANGELOG.md file` check is disabled
