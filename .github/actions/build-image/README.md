## Build images

The image build pipeline consists of a composite GitHub Action and a reusable workflow. Together, they build OCI images from changed Dockerfiles and push them to AWS ECR.

References:
- [Composite action](./action.yaml)
- [Reusable workflow](../../workflows/build-images.yaml)

### Composite action

#### How it works

When invoked for a particular build context and environment, the action performs:

1. Merges the following `.env` files into `.env.merged`, in order, so later values override earlier ones:
   - `.env`
   - `.env.<environment>`
   - `<context>/.env`
   - `<context>/.env.<environment>`

2. Exports variables from `.env.merged` to the job environment.

3. Configures AWS credentials via OIDC (using `aws_region` and `aws_gha_role`) and logs in to the target AWS ECR registry.

4. Optionally authenticates to OCI registries used for base image pulls.

5. Determines the tag for the image:
   - if the Dockerfile contains `ARG IMAGE_TAG=...`, that value is used directly;
   - otherwise, the action reads `ARG IMAGE_SHA=...` and searches the OCI repository specified by `docker_repository` for a non-`latest` tag matching that digest.

6. If the requested build platforms are not exactly the runner's native platform, QEMU and Docker Buildx are configured for multi-platform builds.

7. Builds and pushes the image to AWS ECR using the resolved and `latest` tags.

8. Uploads build metadata for the pull-request comment as an artifact (a JSON file).

9. Sends the build result to Slack using the provided incoming webhook URL.

#### Inputs

- `context` (required): Relative path to the Docker build context (which must contain a Dockerfile).
- `dockerfile` (required): Filename of the Dockerfile.
- `environment` (required): One of `dev`, `staging`, `prod`.
- `slack_webhook_url` (required): Slack Incoming Webhook URL for build result notifications.
- `base_registry` (optional): OCI registry hostname used for authenticated base-image pulls.
- `base_registry_username` (optional): Username for `base_registry`.
- `base_registry_password` (optional): Password, PAT, robot token, or equivalent credential for `base_registry`.
- `base_registries_auth` (optional): Multi-registry authentication configuration. Use this instead of the `base_registry_*` inputs when credentials for more than one registry are required.
- `github_token_login` (optional, default `false`): Authenticate to `ghcr.io` using the job's `GITHUB_TOKEN`.

#### Required environment variables (provided via [.env files listed above](#how-it-works))

- `aws_account`: AWS account ID used for the ECR registry metadata.
- `aws_gha_role`: IAM role to assume via GitHub OIDC for ECR access.
- `aws_region`: AWS region.
- `docker_repository`: OCI repository containing the base image, used for the digest-to-tag fallback lookup, e.g. `paketobuildpacks/builder-jammy-full`, `ghcr.io/actions/actions-runner`.
- `ecr_repository_name`: Name of the target ECR repository.
- `ecr_repository_uri`: Full ECR repository URI, e.g. `123456789012.dkr.ecr.us-east-1.amazonaws.com/repository`.
- `platforms`: Comma-separated list of target platforms, e.g. `linux/amd64,linux/arm64`.

#### Dockerfile requirement

The preferred Dockerfile format declares both the human-readable base image tag and its immutable digest:

```Dockerfile
ARG IMAGE_TAG=v4.0.11
ARG IMAGE_SHA=sha256:4545f6f30e1a27874c6c8a1d5be04fa8c6ada2a8c0b2bdd39e283dd249342e01
FROM quay.io/argoproj/argocli:${IMAGE_TAG}@${IMAGE_SHA}
```

`IMAGE_TAG` is used as the tag of the image published to ECR, while `IMAGE_SHA` keeps the base image pull pinned to an immutable digest.

> [!TIP]
> Both `IMAGE_TAG` and `IMAGE_SHA` should be maintained by Renovate so that base-image updates keep the tag and digest in sync.

For backward compatibility, Dockerfiles that contain only `IMAGE_SHA` are also supported:
- when `IMAGE_TAG` is missing, the action searches the OCI repository specified by `docker_repository` for a tag whose manifest digest matches `IMAGE_SHA`;
- `latest` and digest-derived Cosign tags are excluded from this lookup.

### Reusable workflow

#### How it works

The reusable workflow composes the following jobs:
- `prepare-input-data`
  - checks changed Dockerfiles in the PR
  - reads PR labels `build:*` to prepare a build matrix that looks like this:

```json
{
  "include": [
    {"environment": "dev",  "context": "buildpacks/backend/builder", "dockerfile":"Dockerfile"},
    {"environment": "dev",  "context": "buildpacks/backend/runner",  "dockerfile":"Dockerfile"},
    {"environment": "prod", "context": "buildpacks/backend/builder", "dockerfile":"Dockerfile"},
    {"environment": "prod", "context": "buildpacks/backend/runner",  "dockerfile":"Dockerfile"}
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

#### Workflow call parameters

Inputs:

- `runner` (required): Runner label used to route jobs to specific types of runners (e.g. `ubuntu-latest`).
- `base_registry` (optional, default `docker.io`): OCI registry hostname for single-registry authentication.
- `github_token_login` (optional, default `false`): Authenticate to `ghcr.io` with the caller job's `GITHUB_TOKEN`.

Secrets:

- `base_registry_username` (optional): Username for `base_registry`.
- `base_registry_password` (optional): Password/token for `base_registry`.
- `base_registries_auth` (optional): Multi-registry authentication configuration.
- `slack_webhook_url` (required): Slack Incoming Webhook URL for build result notifications.

### Call the reusable workflow from a repository

We use this workflow to automatically update Docker images with Renovate Bot. To fully configure the workflow for building and publishing Docker images, sending Slack notifications, and automatically merging pull requests opened by Renovate Bot, complete the following steps.

#### 1. Set up Renovate Bot

Allow access to the Saritasa RenovateBot GitHub application in the [organization settings](https://github.com/organizations/saritasa-nest/settings/installations/52274182) and update the bot configuration in `renovate.json5`.

Example configuration for updating buildpack Docker images:

```json5
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
        'build:dev',
        'build:staging',
        'build:prod',
        'build-images',
      ],
    },
  ],
}
```

#### 2. Configure Slack notifications

Create a public Slack channel named `#project-<client>-docker-images` and obtain a Slack incoming webhook for it [here](https://api.slack.com/apps/A01LM626QTZ/incoming-webhooks).

> [!IMPORTANT]
> Store the webhook URL as the `CI_SLACK_WEBHOOK` repository secret.

#### 3. Configure OCI registry authentication

For a single authenticated OCI registry, its credentials can be stored as a pair of repository secrets, e.g. `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`. They can later be passed to the reusable workflow together with the registry hostname:

```yaml
jobs:
  build-images:
    # ...
    with:
      # ...
      base_registry: docker.io  # default value, can be omitted
    secrets:
      # ...
      base_registry_username: ${{ secrets.DOCKERHUB_USERNAME }}
      base_registry_password: ${{ secrets.DOCKERHUB_TOKEN }}
```

If Dockerfiles in the repository use base images from multiple OCI registries, their credentials must be passed via `base_registries_auth`:

```yaml
jobs:
  build-images:
    # ...
    secrets:
      # ...
      base_registries_auth: |
        - registry: docker.io
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
        - registry: quay.io
          username: ${{ secrets.QUAY_USERNAME }}
          password: ${{ secrets.QUAY_PASSWORD }}
```

> [!TIP]
> Use `base_registries_auth` instead of `base_registry`, `base_registry_username`, and `base_registry_password` when authentication to more than one registry is required.

For private images hosted on `ghcr.io`, the workflow can authenticate using the calling job's built-in `GITHUB_TOKEN`, so a separate GHCR credential does not need to be stored as a repository secret:

```yaml
jobs:
  build-images:
    # ...
    with:
      # ...
      github_token_login: true
```

The repository running the workflow must have read access to the private GHCR package. Actions access can be managed in its settings:

```sh
https://github.com/orgs/${org_name}/packages/container/${image_name}/settings
```

#### 4. Add the build-images workflow

Add the `build-images.yaml` workflow that starts when the `build-images` label is added to a pull request opened by Renovate Bot:

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
# │                                                                                                                                                      │
# │ The workflow needs the following environment variables:                                                                                              │
# │ - `aws_account` - AWS account ID for the current environment                                                                                         │
# │ - `aws_gha_role` - role for access to AWS using the GitHub OIDC provider                                                                             │
# │ - `aws_region` - the region in which the ECR for the custom image is located                                                                         │
# │ - `client` - project name                                                                                                                            │
# │ - `docker_repository` - OCI repository containing the base image that is referenced by the Dockerfile                                                │
# │ - `ecr_repository_name` - AWS ECR repository name for custom images                                                                                  │
# │ - `ecr_repository_uri` - AWS ECR repository URI for custom images                                                                                    │
# │ - `platforms` - list of target platforms for the build                                                                                               │
# │                                                                                                                                                      │
# │ These variables can be loaded from the following files:                                                                                              │
# │ - .env                                                                                                                                               │
# │ - .env.<environment>                                                                                                                                 │
# │ - <context>/.env                                                                                                                                     │
# │ - <context>/.env.<environment>                                                                                                                       │
# │                                                                                                                                                      │
# │ A separate job is launched for each image. It builds the image, publishes it to AWS ECR, and sends a notification                                    │
# │ to the Slack channel `project-<client>-docker-images`. After all builds complete, the workflow creates or updates a PR comment.                      │
# │ If all builds succeed, the workflow adds the `auto-merge` label, allowing the PR to be merged by Mergeable.                                          │
# │                                                                                                                                                      │
# │ Authorization into AWS is performed using the GitHub OIDC provider:                                                                                  │
# │ https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services │
# │                                                                                                                                                      │
# │ If the repository uses base images from Docker Hub, it is recommended to configure authentication to avoid exceeding rate limits.                    │
# │ Create a separate read-only PAT for the project in the Docker Hub settings:                                                                          │
# │ https://keys.saritasa.cloud/cred/detail/jcVFhPTvQ9DBsomCJ83BPf/                                                                                      │
# │                                                                                                                                                      │
# │ Get a Slack webhook URL to send notifications to the Slack channel:                                                                                  │
# │ https://api.slack.com/apps/A01LM626QTZ/incoming-webhooks                                                                                             │
# │                                                                                                                                                      │
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
    uses: saritasa-nest/saritasa-github-actions/.github/workflows/build-images.yaml@v7.0
    with:
      runner: saritasa-rocks-eks
    secrets:
      base_registry_username: ${{ secrets.DOCKERHUB_USERNAME }}
      base_registry_password: ${{ secrets.DOCKERHUB_TOKEN }}
      slack_webhook_url: ${{ secrets.CI_SLACK_WEBHOOK }}
```

Adjust the registry authentication inputs and secrets according to the repository's needs. See the section above for details.

#### 5. Add changelog automation

Add the [add-changelog-entry](../add-changelog-entry/action.yml) action to update the changelog after merging a PR to the main branch.

#### 6. Configure Mergeable

Configure the required Mergeable checks in `.github/mergeable.yml` so that Renovate PRs containing Docker image updates can follow the automated build and merge process.

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

  # Require Code Owner approval for all PRs except Renovate PRs
  # that update Dockerfiles
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
                  message: Do not require approvals for Renovate PRs that update Dockerfiles
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

#### 7. Configure repository labels and rulesets

Add the build labels to the `.github/settings.yaml` file:

```yaml
labels:
  - name: build-images
    color: 43C0F2
    description: Trigger the build-images workflow
  - name: build:dev
    color: 006B75
    description: Build OCI images for the dev environment
  - name: build:staging
    color: 006B75
    description: Build OCI images for the staging environment
  - name: build:prod
    color: 006B75
    description: Build OCI images for the prod environment
  - name: auto-merge
    color: D8F7B2
    description: Allow the PR to be merged automatically
```

The following ruleset values in `.github/settings.yaml` are required for the workflow to operate correctly:

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
