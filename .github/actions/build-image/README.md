## Build images

The image build pipeline consists of a composite GitHub Action and a reusable workflow. Together, they build Docker images and push them to AWS ECR.

References:
- [Composite action](./action.yaml)
- [Reusable workflow](../../workflows/build-images.yaml)

### Composite action

#### How it works

When invoked for a particular build context and environment, the action performs:

1) Combine env files into `.env.common` using the following order:
    - `.env`
    - `.env.<environment>`
    - `<context>/.env`
    - `<context>/.env.<environment>`

2) Export variables from `.env.common` to the job environment.

3) Configure AWS credentials via OIDC using `aws_region` and `aws_gha_role`.

4) Log in to AWS ECR.

5) Determine the image tag to use by reading `ARG IMAGE_SHA=...` from `<context>/Dockerfile` and finding the matching tag in Docker Hub for the repo specified by `docker_repository` (optionally authenticated to avoid rate limits).

6) Build and push the Docker image to ECR with two tags: the discovered tag and `latest`.

7) Prepare a JSON file with build metadata (account, region, repo, digest) and upload it as an artifact for PR commenting.

8) Send a Slack notification (success/failure) to the provided incoming webhook URL.

#### Inputs

- `context` (required): Relative path to the folder that contains the `Dockerfile` and build context.
- `environment` (required): One of `dev`, `staging`, `prod`.
- `slack_webhook_url` (required): Slack Incoming Webhook URL to post build status.
- `dockerhub_username` (optional): Docker Hub username for read-only auth (reduces rate limits when querying tags).
- `dockerhub_token` (optional): Docker Hub token.

#### Required environment variables (provided via env files listed above)

- `aws_account`: AWS account ID used for the ECR registry metadata.
- `aws_gha_role`: IAM role to assume via GitHub OIDC for ECR access.
- `aws_region`: AWS region.
- `docker_repository`: Source Docker Hub repository used by your Dockerfile.
- `ecr_repository_name`: Name of the target ECR repository.
- `ecr_repository_uri`: Full ECR repository URI, e.g. `123456789012.dkr.ecr.us-east-1.amazonaws.com/repository`.
- `platforms`: Comma-separated list of target platforms, e.g. `linux/amd64,linux/arm64`.

#### Dockerfile requirement

Your `<context>/Dockerfile` must contain a line with the base image digest:

```Dockerfile
ARG IMAGE_SHA=sha256:...
```

The action will fetch a non-`latest` tag from Docker Hub whose digest matches `IMAGE_SHA` in the repository defined by `docker_repository`. That tag is then used as the version for the built ECR image.

### Reusable workflow

#### How it works

The reusable workflow composes the following jobs:
- `prepare-input-data`
  - checks changed Dockerfiles in the PR
  - reads PR labels `build:*` to prepare a build matrix that looks like this:

```json
{
  "include": [
    {"environment": "dev", "context": "buildpacks/backend/builder"},
    {"environment": "dev", "context": "buildpacks/backend/runner"},
    {"environment": "prod", "context": "buildpacks/backend/builder"},
    {"environment": "prod", "context": "buildpacks/backend/runner"}
  ]
}
```

- `build-images`
  - for each matrix entry, calls the composite action to build and push the Docker image
- `create-pr-comment`
  - merges all artifacts into a single data file
  - renders a PR comment from a Jinja2 template ([pr-comment-template.j2](pr-comment-template.j2)) with build results
- `add-auto-merge-label`
  - if everything succeeded, adds the `auto-merge` label to the PR

#### Inputs and secrets

Workflow inputs and secrets (workflow_call):

- inputs:
  - `runner` (required): Runner label to execute jobs on, e.g. `ubuntu-latest` or a self-hosted label.
- secrets:
  - `dockerhub_username` (optional): Docker Hub username for read-only auth (reduces rate limits when querying tags).
  - `dockerhub_token` (optional): Docker Hub token.
  - `slack_webhook_url` (required): Slack Incoming Webhook URL to post build status.

### Call the reusable workflow from a repository

We use this workflow to automatically update Docker images with Renovate Bot. To fully configure the process that builds and publishes a Docker image, sends a notification to the Slack channel, and merges PRs opened by Renovate Bot, follow these steps:

1. Set up Renovate bot for your repository.
Allow access to the Saritasa RenovateBot GitHub application in the [organization settings](https://github.com/organizations/saritasa-nest/settings/installations/52274182) and then update the bot configuration in file `renovate.json5`.
Example configuration for updating buildpack Docker images:

```
{
  packageRules: [
    {
      // Add `build:dev`, `build:staging`, `build:prod` labels to PRs containing changes in buildpack Dockerfiles
      // The `build-images` label starts the GitHub workflow that builds and publishes Docker images
      matchManagers: [
        'dockerfile',
      ],
      matchFileNames: [
        'buildpacks/**',
      ],
      labels: [
        'build:dev', 'build:staging', 'build:prod',
        'build-images',
      ],
    },
  ],
}
```

2. Create a public Slack channel `#project-<client>-docker-images` and obtain a Slack webhook for it [here](https://api.slack.com/apps/A01LM626QTZ/incoming-webhooks).

3. Add `DOCKERHUB_TOKEN`, `DOCKERHUB_USERNAME`, `CI_SLACK_WEBHOOK` to repository secrets.

4. Add `build-images.yaml` workflow that will be started when the `build-images` label is added to the PR opened by the Renovate bot:

```yaml
---
# ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
# │ Build images workflow                                                                                                                                │
# │                                                                                                                                                      │
# │ This workflow is designed to automatically build custom Docker images defined in this repository.                                                    │
# │ It is launched in pull requests created by the Renovate bot.                                                                                         │
# │ To start the workflow, add the `build-images` label to the pull request.                                                                             │
# │ The workflow extracts environments for which images need to be built from the labels `build:dev`, `build:staging`, `build:prod`.                     │
# │ Then the workflow checks which images' Dockerfiles were changed and builds and publishes them.                                                       │
# │ The workflow needs the following environment variables:                                                                                               │
# │ - `aws_account` - AWS account ID for the current environment                                                                                          │
# │ - `aws_gha_role` - role for access to AWS using the GitHub OIDC provider                                                                              │
# │ - `aws_region` - the region in which the ECR for the custom image is located                                                                         │
# │ - `client` - project name                                                                                                                            │
# │ - `docker_repository` - the base image used in the Dockerfile on which the custom image is based                                                     │
# │ - `ecr_repository_name` - AWS ECR repository name for custom images                                                                                  │
# │ - `ecr_repository_uri` - AWS ECR repository URI for custom images                                                                                    │
# │ - `platforms` - list of target platforms for the build                                                                                               │
# │ These variables can be loaded from the following files:                                                                                              │
# │ - .env                                                                                                                                               │
# │ - .env.<environment>                                                                                                                                 │
# │ - <context>.env                                                                                                                                      │
# │ - <context>.env.<environment>                                                                                                                        │
# │                                                                                                                                                      │
# │ A separate job is launched for each image. It builds the image, publishes it to AWS ECR, and sends a notification                                     │
# │ to the Slack channel `project-<client>-docker-images`. After all builds are completed, a comment is created in the pull request.                     │
# │ If the build is successful, the workflow will add an `auto-merge` label allowing automatic PR merge, and the PR will be merged by Mergeable.         │
# │                                                                                                                                                      │
# │ Authorization into AWS is performed using the GitHub OIDC provider:                                                                                  │
# │ https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services │
# │                                                                                                                                                      │
# │ Log in to Docker Hub with the `saritasa-infra-v2-ro` token to avoid issues with exceeding request limits:                                            │
# │ https://keys.saritasa.cloud/cred/detail/jcVFhPTvQ9DBsomCJ83BPf/                                                                                      │
# │                                                                                                                                                      │
# │ Get a Slack webhook URL to send notifications to the Slack channel:                                                                                  │
# │ https://api.slack.com/apps/A01LM626QTZ/incoming-webhooks                                                                                             │
# │                                                                                                                                                      |
# └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
name: build-images

on:
  pull_request:
    types:
      - labeled

jobs:
  build-images:
    if: |
      github.event.pull_request.user.login == 'saritasa-renovatebot[bot]' &&
      github.event.label.name == 'build-images'
    uses: saritasa-nest/saritasa-github-actions/.github/workflows/build-images.yaml@v4.5
    with:
      runner: saritasa-rocks-eks
    secrets:
      dockerhub_token: ${{ secrets.DOCKERHUB_TOKEN }}
      dockerhub_username: ${{ secrets.DOCKERHUB_USERNAME }}
      slack_webhook_url: ${{ secrets.CI_SLACK_WEBHOOK }}
```

5. Add [add-changelog-entry](../add-changelog-entry/action.yml) action to update the changelog after merging a PR to the main branch.

6. These Mergeable checks in the `.github/mergeable.yml` file must be configured as follows for the workflow to work correctly:

```yaml
mergeable:
  # CHANGELOG.md is required in the PR
  - when: >-
      pull_request.opened,
      pull_request.synchronize,
      pull_request.reopened
    name: Checking for the presence of the CHANGELOG.md file
    validate:
      - do: or
        validate:
          - do: changeset
            no_empty:
              enabled: true
            must_include:
              regex: CHANGELOG.md
              message: CHANGELOG.md with details must be present in every PR by an author
          - do: author
            must_include:
              regex: ^saritasa-renovatebot
              message: Exclude CHANGELOG.md change for renovate bot

  # Require Code Owner approval for all PRs except renovate PRs
  # that update the backend buildpacks
  - when: pull_request.*, pull_request_review.*
    name: Approvals check
    validate:
      - do: or
        validate:
          - do: approvals
            min:
              count: 1
              message: At minimum 1 person are required to review this PR before merging
            block:
              changes_requested: true
              message: You have open changes requested from the reviewers
            limit:
              # the file .github/CODEOWNERS is read and only owners approval will count
              owners: true
          - do: and
            validate:
              - do: author
                must_include:
                  regex: ^saritasa-renovatebot
                  message: Do not require approvals for renovate prs that update docker images
              - do: label
                must_include:
                  regex: ^build-images
                  regex_flag: i

  # Auto-merge PR when all required checks have passed and all reviewers approved
  - when: pull_request_review.submitted, check_suite.completed
    name: All checks pass, auto-merge
    filter:
      - do: author
        must_exclude:
          regex: ^saritasa-renovatebot
    validate:
      - do: baseRef
        must_include:
          regex: main
          message: Auto-merge is only supported for the default branch
        mediaType:
          previews:
            - groot
      - do: approvals
        required:
          reviewers:
            # add primary devops engineer of the projects
            - dmitry-mightydevops
            - kseniyashaydurova
        block:
          changes_requested: true
          message: Auto-merge is not allowed if changes are requested
    pass:
      - do: merge
        merge_method: squash

  # Merge PR created by Renovate bot if the `auto-merge` label is added
  - when: pull_request.labeled
    name: Auto-merge renovate prs
    filter:
      - do: author
        must_include:
          regex: ^saritasa-renovatebot
    validate:
      - do: label
        must_include:
          regex: auto-merge
          regex_flag: i  # case-insensitive (it is a default, to disable use 'none')
          message: Merging is not allowed if the `auto-merge` label is missing
    pass:
      - do: merge
        merge_method: squash
```

7. Add the necessary labels to the `.github/settings.yaml` file:

```yaml
---
labels:
  - name: build:dev
    color: 006B75
    description: Build images with github action for dev env
  - name: build:prod
    color: 006B75
    description: Build images with github action for prod env
  - name: build:staging
    color: 006B75
    description: Build images with github action for staging env
  - name: auto-merge
    color: D8F7B2
    description: Allow auto-merge pr
  - name: build-images
    color: 43C0F2
    description: Run buildpack docker images build
```

Also the following values in the rulesets in the `.github/settings.yaml` file are required for the correct operation of the workflow:

```yaml
rulesets:
  - name: branch-protection
    bypass_actors:
      # saritasa-changelog github app
      # Manage app: https://github.com/organizations/saritasa-nest/settings/apps/saritasa-changelog
      - actor_id: 1174212
        actor_type: Integration
        bypass_mode: always
    rules:
      - type: pull_request
        parameters:
          require_code_owner_review: false
          required_approving_review_count: 0
      - type: required_status_checks
        parameters:
          required_status_checks:
            - context: 'Mergeable: Approvals check'
              integration_id: 408776
```

### GitHub OIDC provider

Authorization into AWS is performed using the GitHub OIDC provider: <https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services>.

It is configured in the `platforms/github/actions` stack in the infra-aws repository.
