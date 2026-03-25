# Changelog

## 2026-03-25

[v5.4]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/38)
- Excluded `CHANGELOG.md` and `README.md` files from PR summary analysis in `pr-summary` action

## 2026-03-23

[v5.3]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/37)
- Added `client_session_timeout_seconds` for MCP server in `pr-summary` action; 
- Added code changes size limit with truncation to prevent exceeding model context window

## 2026-03-20

[v5.2]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/36)
- Updated `aquasecurity/trivy-action` to `0.35.0` version

## 2026-03-02

[v4.9]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/33)
- Updated trivy version to `v0.69.2` in `security-audit` action

## 2025-10-06

[v4.7]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/31)
- Adaptation of the `build-image` action for use in `saritasa-devops-docker-images`

[v4.6]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/30)
- Updated prompt for `pr-summary` action

## 2025-09-29

[v4.5]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/29)
- Fixed extraction of PR comment template for `build-images` workflow

## 2025-09-02

[v4.4]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/27)
- Added `build-images` workflow

## 2025-09-16

[v4.3]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/28)
- Added `pr-summary` action

## 2025-03-14

[v3.4]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/18)
- Deleted `updates-dependencies-python` action

[v3.4]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/17)
- Added `pre-commit` composite action

## 2025-02-12

[v3.3]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/15)
- Added summary for action with information about the result of `secrets-checks`

## 2025-01-30

[v3.2]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/14)
- Added variable `enable-pr-comment` for `secrets-checks`, allowing to disable PR check comment.
  Used for .NET projects where the comment is unnecessary for developers.

## 2024-11-25

[v3.1]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/13)
- Update `trivy`check

## 2024-10-30

[v2.9-dev.1]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/11)
- In ci-asp-app.yaml workflow updated steps `Upload artifact for deployment task` and `Download artifact from build task`
  to fix an error that occurs when using `actions/upload-artifact` and `actions/download-artifact` workflows.

## 2024-08-21

[v2.8]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/10)
- Add `secrets-checks` action

## 2024-03-29

[v2.6]

- [associated PR](https://github.com/saritasa-nest/saritasa-github-actions/pull/8)
- Update `fastlane-android` action - update 3rd party steps to actual versions (get rid of deprecated warnings)
- Build android apps on self-hosted github runners in Rocks cluster
- Fix `google-services.json` file creation
- Fix warning about UTF-8 locale required for fastlane
