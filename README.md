# saritasa-github-actions
GitHub actions

## CI-wordpress reusable workflow

### Inputs variables

| Variable       | Type          | Example                  | Discription                                                     |
| ---------------|:-------------:| :------------------------|-----------------------------------------------------------------|
| server_host    | string        | 59.128.16.24             | The address of the server for deploy                            |
| environment    | string        | production               | The environment for deploy i.e development, staging, production |
| playbook_path  | string        | ci/ansible/playbook.yaml | The path to the file relative to the repository, used in Ansistrano deploy task |
| deploy_path    | string        | ~/deploy/                | The path to deploy on the remote server |
| deploy_repo    | string        | git@github.com:saritasa-nest/ceai-wordpress.git | The path to deploy on the remote server |
| deploy_branch  | string        | develop | The branch from which the deployment is made  |
| python_version | number        | 3.11.4 | Each python version supports a certain range of ansible versions, so we need to specify the current version of python in order to install the latest version of ansible. |
| runner         | string        | ubuntu-latest | The runner on which workflow is running: ubuntu, macos, windows, etc |

### Inputs secrets

| Variable       | Discription                                                    |
| ---------------|:---------------------------------------------------------------|
| ssh_private_key | The private key for connect to production server via ssh      |

### Examples

```bash
name: Deploy to Bluehost
on:
  push:
    branches:
      - feature/add-ci

  workflow_dispatch:

jobs:
  deploy:
    uses: saritasa-nest/saritasa-github-actions/.github/workflows/ci-wordpress.yaml@v2.4-dev.1
    with:
      ENVIRONMENT: production                                      # The Environment for deploy
      SERVER_HOST: 50.87.253.20                                    # The pruduction server
      SSH_DEPLOY_USER: ${{ vars.SSH_DEPLOY_USER }}                 # The username for for connect to production server via ssh
      PLAYBOOK_PATH: ci/ansible/ansistrano-deploy.yml              # The path to the file relative to the repository
      DEPLOY_PATH: ~/deploy/                                       # The path to deploy on the production server
      DEPLOY_REPO: git@github.com:saritasa-nest/ceai-wordpress.git # The repository for deploy
      DEPLOY_BRANCH: develop                                       # The branche for deploy
      PYTHON_VERSION: 3.11                                         # The version of python
      RUNNER: ubuntu-latest                                        # The type of github runner

    secrets:
      ssh_private_key: ${{ secrets.SSH_PRIVATE_KEY }}

```

### Ansistrano deploy playbook

```bash
---
- name: deployment
  hosts: all
  vars:
    ansistrano_keep_releases: 10
    ansistrano_deploy_from: "{{ playbook_dir }}/.."
    ansistrano_deploy_to: "{{ deploy_path }}"
    ansistrano_git_repo: "{{ deploy_repo }}"
    ansistrano_git_branch: "{{ deploy_branch }}"
    ansistrano_deploy_via: "git"
    ansistrano_git_depth: 1
    ansistrano_shared_paths:
      - wp-content/uploads
      - .well-known
      - cgi-bin
    ansistrano_shared_files:
      - wp-config.php
      - .htaccess
  roles:
      - { role: ansistrano.deploy }
```
`ansistrano_keep_releases` number of stored releases default 3

`ansistrano_deploy_from` where my local project is (relative or absolute path)

`ansistrano_deploy_to` base path to deploy to

`ansistrano_git_repo` location of the git repository

`ansistrano_git_branch` what version of the repository to check out. This can be the full 40-character SHA-1 hash, the literal string HEAD, a branch name, or a tag name

`ansistrano_deploy_via` deployment strategy - method used to deliver code. Options are copy, download, git, rsync, rsync_direct, svn, or s3.

`ansistrano_git_depth` additional history truncated to the specified number or revisions

`ansistrano_shared_paths` shared folders, usually folders with images or other bulk data

`ansistrano_shared_files` files that should not get into the repository are not necessary for the work of Wordpress


More information for adnsistrano playbook in official [docs](https://github.com/ansistrano/deploy/blob/master/README.md)
