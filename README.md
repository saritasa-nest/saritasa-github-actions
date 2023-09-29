# Workflows
## android
## asp.net
## ios

## wordpress
### ci-wordpress reusable workflow

### Deploying

In order to deploy, you need to perform some steps:

- Create a new workflow file for deploying your app, for example, [`deploy.yml`](https://github.com/saritasa-nest/ceai-wordpress/blob/develop/.github/workflows/ci-prod.yml)
- Place the created playbook in your repository for example, [`ci\ansible\deploy.yaml`](https://github.com/saritasa-nest/ceai-wordpress/blob/develop/ci/ansible/ansistrano-rollback.yml)
- Set up variables for workflow (see [Inputs Variables](#inputs-variables))
- Create a workflow, configure workflow start triggers (see examles)

Watch the [video](https://vimeo.com/manage/videos/869032249)

During deployment, ansistrano looks at the current timestamp in runner by executing `date -u +%Y%m%d%H%M%SZ`. Each new release is placed in a folder with a name consisting of the previously received timestamp.

If everything has been set up properly, after completing the workflow approximately the following structure will be created on the server.
Check how the on your server folder structure would look like after one, two and three deployments.

```
-- /var/www/my-app.com
|-- current -> /var/www/my-app.com/releases/20100509145325
|-- releases
|   |-- 20100509145325
|-- shared
```

```
-- /var/www/my-app.com
|-- current -> /var/www/my-app.com/releases/20100509150741
|-- releases
|   |-- 20100509150741
|   |-- 20100509145325
|-- shared
```

```
-- /var/www/my-app.com
|-- current -> /var/www/my-app.com/releases/20100512131539
|-- releases
|   |-- 20100512131539
|   |-- 20100509150741
|   |-- 20100509145325
|-- shared
```

### Rolling back

In order to rollback, you need to set up the deployment and run the rollback workflow. Workflow, will switch the current folder to the previous release.
- Create a new workflow file for rollback, for example, [`rollback.yml`](https://github.com/saritasa-nest/ceai-wordpress/blob/develop/.github/workflows/ci-rollback.yml)
- Place the created playbook in your repository for example, [`ci\ansible\rollback.yaml`](https://github.com/saritasa-nest/ceai-wordpress/blob/develop/ci/ansible/ansistrano-deploy.yml)

Watch the [video](https://vimeo.com/manage/videos/869032751)

Before rollback
```
-- /var/www/my-app.com
|-- current -> /var/www/my-app.com/releases/20100512131539
|-- releases
|   |-- 20100512131539
|   |-- 20100509150741
|   |-- 20100509145325
|-- shared
```

After rollback
```
-- /var/www/my-app.com
|-- current -> /var/www/my-app.com/releases/20100509150741
|-- releases
|   |-- 20100509150741
|   |-- 20100509145325
|-- shared
```

### Inputs variables

| Variable       | Type          | Example                  | Discription                                                                                                       |
| ---------------|:-------------:| :------------------------|-------------------------------------------------------------------------------------------------------------------|
| server_host    | string        | 59.128.16.24             | The address of the server for deploy                                                                              |
| environment    | string        | production               | The environment for deploy i.e development, staging, production                                                   |
| playbook_path  | string        | ci/ansible/playbook.yaml | The path to the file relative to the repository from which the deployment is made, used in Ansistrano deploy task |
| deploy_path    | string        | ~/deploy/                | The path to deploy on the remote server                                                                           |
| deploy_repo    | string        | git@github.com:saritasa-nest/ceai-wordpress.git | The path to deploy on the remote server                                                    |
| deploy_branch  | string        | develop                  | The branch from which the deployment is made                                                                      |
| python_version | number        | 3.11.4 | Each python version supports a certain range of ansible versions, so we need to specify the current version of python in order to install the latest version of ansible. |
| runner         | string        | saritasa-rocks-eks       | The runner on which workflow is running: ubuntu, macos, windows, etc                                              |

### Inputs secrets

| Variable        | Discription                                                    |
| ----------------|:---------------------------------------------------------------|
| ssh_private_key | The private key for connect to server via ssh                  |

### Examples

#### Workflow for deploy

Watch the [video](https://vimeo.com/manage/videos/869032249)

This implementation is used in the [CEAI-Wordpress project](https://github.com/saritasa-nest/ceai-wordpress/tree/main/.github/workflows) project to deploy Wordpress on shared hosting.

`ci-prod.yml`

```bash
name: Deploy to Bluehost
on:
  workflow_dispatch:

jobs:
  deploy:
    uses: saritasa-nest/saritasa-github-actions/.github/workflows/ci-wordpress.yaml@v2.4
    with:
      ENVIRONMENT: production                                      # The Environment for deploy
      HOST: 50.87.253.20                                           # The server for deploy
      USER: ${{ vars.SSH_DEPLOY_USER }}                            # The username for connect to server via ssh
      PLAYBOOK_PATH: ci/ansible/ansistrano-deploy.yml              # The path to the file relative to the repository from which the deployment is made
      DEPLOY_PATH: ~/deploy/                                       # The path to deploy on the server
      DEPLOY_REPO: git@github.com:saritasa-nest/ceai-wordpress.git # The repository for deploy
      DEPLOY_BRANCH: develop                                       # The branch for deploy
      PYTHON_VERSION: 3.11                                         # The version of python
      RUNNER: saritasa-rocks-eks                                   # The type of github runner

    secrets:
      ssh_private_key: ${{ secrets.SSH_PRIVATE_KEY }}

```

### Ansistrano deploy playbook

`ansistrano-deploy.yml`

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

#### Workflow for rollback for one step back

Watch the [video](https://vimeo.com/manage/videos/869032751)

`ci-rollback.yml`

```bash
name: Rollback to Previously release
on:
  workflow_dispatch:

jobs:
  deploy:
    uses: saritasa-nest/saritasa-github-actions/.github/workflows/ci-wordpress.yaml@v2.4
    with:
      ENVIRONMENT: production                                      # The Environment for deploy
      HOST: 50.87.253.20                                           # The remote server
      USER: ${{ vars.SSH_DEPLOY_USER }}                            # The username to connect to server via ssh
      PLAYBOOK_PATH: ci/ansible/ansistrano-rollback.yml            # The path to the file relative to the repository from which the deployment is made
      DEPLOY_PATH: ~/deploy/                                       # The path to deploy on the server
      PYTHON_VERSION: 3.11                                         # The version of python
      RUNNER: saritasa-rocks-eks                                   # The type of github runner

    secrets:
      ssh_private_key: ${{ secrets.SSH_PRIVATE_KEY }}
```

### Ansistrano rollback playbook

`ansistrano-rollback.yml`

```bash
---
- name: rollback
  hosts: all
  vars:
    ansistrano_deploy_to: "{{ deploy_path }}"
  roles:
      - { role: ansistrano.rollback }
```

More information for adnsistrano playbook in official [docs](https://github.com/ansistrano/deploy/blob/master/README.md)
