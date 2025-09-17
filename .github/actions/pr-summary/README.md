# PR Summary Generator

A GitHub Action that automatically generates and updates pull request descriptions using OpenAI's language models. This action analyzes code changes, extracts JIRA tasks, and creates a clean, informative PR summary.

## Features

- Automatically generates PR summaries using OpenAI's language models
- Extracts and links JIRA tasks from commit messages
- Updates PR descriptions with the generated summary

## Inputs

| Input            | Required | Default                          | Description                                    |
| ---------------- | -------- | -------------------------------- | ---------------------------------------------- |
| `github-token`   | Yes      | -                                | GitHub token for API access                    |
| `openai-api-key` | Yes      | -                                | OpenAI API key for PR summary generation       |
| `pr-number`      | Yes      | -                                | PR number to update with the generated summary |
| `jira-url`       | No       | `https://saritasa.atlassian.net` | Base URL for JIRA instance                     |
| `openai-model`   | No       | `gpt-5`                          | OpenAI model to use for summary generation     |
| `openai-prompt`  | No       | [See below](#prompt-example)     | Custom prompt template for OpenAI              |

## OpenAI API Key

The OpenAI API key is stored at the organization level and is available to all private repositories. You can access the token value here: https://keys.saritasa.cloud/cred/detail/Yfe98Px2yLH3tCjLYvPAHb/

## Usage

### Basic Example

```yaml
---
name: Autogenerate PR Summary

on:
  pull_request:
    types:
      - opened
      - ready_for_review

permissions:
  contents: read
  pull-requests: write

jobs:
  auto-generate-summary:
    runs-on: saritasa-rocks-eks
    # Summary will not be generated if the PR was opened as a draft
    if: |
      github.event.pull_request.draft == false
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          ref: ${{github.event.pull_request.head.ref}}
          fetch-depth: 0

      - name: Autogenerate PR summary
        uses: saritasa-nest/saritasa-github-actions/.github/actions/pr-summary@v4.3
        with:
          github-token: ${{secrets.github_token}}
          openai-api-key: ${{secrets.openai_api_key}}
          pr-number: ${{github.event.pull_request.number}}
```

You can customize the AI prompt by providing your own template:

### Prompt Example

```yaml
- name: Autogenerate PR summary with custom prompt
  uses: saritasa-nest/saritasa-github-actions/.github/actions/pr-summary@v4.3
  with:
    github-token: ${{secrets.github_token}}
    openai-api-key: ${{secrets.openai_api_key}}
    pr-number: ${{github.event.pull_request.number}}
    openai-prompt: >-
      Summarize the following code changes as if explaining to a teammate what is new and why it matters.
      - Focus only on files with meaningful or functional changes; skip trivial or empty files.
      - Limit description to one sentence per file.
      - Use bullet points starting with '-' and a space.
      - Combine related changes into one bullet if they belong to the same feature or goal.
      - Vary your wording; avoid repeating "Added/Created" for each bullet.
      - Documentation files changed: {doc_files}. For documentation files, provide a brief summary like "Updated documentation for [feature]" without detailed code diff analysis.

      Changed files:
      {all_files}

      Code changes:
      {code_changes}

      Your response (start with bullet points immediately):
```

## How It Works

1. The action is triggered on pull request events, `ready_for_review` and `opened` (if PR is not a draft)
2. It fetches the PR details and associated commits
3. Extracts JIRA task keys from commit messages
4. Uses OpenAI to analyze the code changes and generate a summary
5. Updates the PR description with the generated summary and JIRA links
