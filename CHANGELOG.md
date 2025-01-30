# Changelog

## 2025-01-30

[3.2]

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
