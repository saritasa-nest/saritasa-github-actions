### Trivy

[Trivy](https://github.com/aquasecurity/trivy-action) finds unencrypted secrets and vulnerabilities in the repository code. Trivy check looks at the current state of files in the repository

We use trivy with this parameters:
- `scan-type: "fs"` - type of scan (`image` - scans docker image; `fs` - scans the file system)
- `scan-ref: "."` - scan reference(current working directory)
- `format: sarif` - file format with scan results
- `exit-code: 1` - exit code when vulnerabilities are found (default `0`)
- `output: "trivy-results.sarif"` - file name with scan results
- `severity: HIGH,CRITICAL` - only report vulnerabilities with HIGH or CRITICAL severity levels (other levels such as LOW and MEDIUM will be ignored)
- env `TRIVY_DB_REPOSITORY: public.ecr.aws/aquasecurity/trivy-db:2` to avoid GitHub Container Registry (GHCR) rate limits and ensure consistent access to Trivy's vulnerability database.

### Gitleaks

[Gitleaks](https://github.com/gitleaks/gitleaks) is a tool for detecting and preventing hardcoded secrets (i.e. ssh pem keys, our files ending with .secrets) exposed in open text in the repository. Gitleaks check the contents of files that were changed in a commit

We use the default Gitleaks configuration (`useDefault = true`), which enables detection of a wide range of common secret patterns out of the box.
You can find more details about the default rules here: https://github.com/zricethezav/gitleaks/blob/master/config/gitleaks.toml

#### environment variables

* `github-token: ${{secrets.GITHUB_TOKEN}}` \
  GitHub token used to authenticate API requests. Use the default GitHub Actions token: `${{ secrets.GITHUB_TOKEN }}`.

* [`gitleaks-license: ${{secrets.GITLEAKS_LICENSE}}`](https://keys.saritasa.cloud/cred/detail/c6nP9FFoXhtxEjKJADwsYQ) \
  To use gitleaks in an organization, we need license key, get here https://gitleaks.io/products.html

    1) go to fill out the Google form
    2) paste devops@saritasa.com into the email field
    3) wait for the key, add it to GitHub at the organization level https://github.com/organizations/saritasa-nest/settings/secrets/actions

* `gitleaks-slack-webhook: ${{secrets.GITLEAKS_SLACK_WEBHOOK}}` \
  The webhook used to send secret scan results to the Slack channel `team-devops-expose-secrets`. Created here: https://api.slack.com/apps/A02F9HK5W21/incoming-webhooks

### Output formatting

after completing trivy and gitleaks checks we get `trivy-results.sarif` and `results.sarif` files

`data.json` is generated based on `trivy-results.sarif` and `results.sarif` files and contains the information about unencrypted secrets to generate a message in slack and PR

Example `data.json`:
```
{
  "gitleaks": {
    "files": [
      {
        "name": "app/key.pem",
        "commitSha": "4403b2177e48c1c06f27d27001c0e757a8409cac",
        "startLine": 1,
        "endLine": 1,
        "secretType": "*.pem"
      },
      {
        "name": "app/key.pem",
        "commitSha": "806ac79714289aba92529a05157466405bfe98f6",
        "startLine": 1,
        "endLine": 1,
        "secretType": "*.pem"
      },
      {
        "name": "app/config.yaml",
        "commitSha": "b0d1cd4de960563a3059513a0ee54340d4d7a331",
        "startLine": 8,
        "endLine": 8,
        "secretType": "github-fine-grained-pat"
      },
      {
        "name": "app/config.yaml",
        "commitSha": "b0d1cd4de960563a3059513a0ee54340d4d7a331",
        "startLine": 4,
        "endLine": 4,
        "secretType": "slack-web-hook"
      }
    ]
  },
  "trivy": {
    "totalSecrets": "2",
    "results": [
      {
        "name": "github-fine-grained-pat",
        "level": "error",
        "severity": "CRITICAL",
        "files": [
          {
            "name": "app/config.yaml",
            "startLine": 8,
            "endLine": 8
          }
        ]
      },
      {
        "name": "slack-web-hook",
        "level": "warning",
        "severity": "MEDIUM",
        "files": [
          {
            "name": "app/config.yaml",
            "startLine": 4,
            "endLine": 4
          }
        ]
      }
    ],
    "details": {
      "driver": {
        "fullName": "Trivy Vulnerability Scanner",
        "informationUri": "https://github.com/aquasecurity/trivy",
        "name": "Trivy",
        "rules": [
          {
            "id": "github-fine-grained-pat",
            "name": "Secret",
            "shortDescription": {
              "text": "GitHub Fine-grained personal access tokens"
            },
            "fullDescription": {
              "text": " name\n  title: title\n  token: *********************************************************************************************sdf\n"
            },
            "defaultConfiguration": {
              "level": "error"
            },
            "helpUri": "https://github.com/aquasecurity/trivy/blob/main/pkg/fanal/secret/builtin-rules.go",
            "help": {
              "text": "Secret GitHub Fine-grained personal access tokens\nSeverity: CRITICAL\nMatch:  name\n  title: title\n  token: *********************************************************************************************sdf\n",
              "markdown": "**Secret GitHub Fine-grained personal access tokens**\n| Severity | Match |\n| --- | --- |\n|CRITICAL| name\n  title: title\n  token: *********************************************************************************************sdf\n|"
            },
            "properties": {
              "precision": "very-high",
              "security-severity": "9.5",
              "tags": [
                "secret",
                "security",
                "CRITICAL"
              ]
            }
          },
          {
            "id": "slack-web-hook",
            "name": "Secret",
            "shortDescription": {
              "text": "Slack Webhook"
            },
            "fullDescription": {
              "text": "  slack: *******************************************************************************"
            },
            "defaultConfiguration": {
              "level": "warning"
            },
            "helpUri": "https://github.com/aquasecurity/trivy/blob/main/pkg/fanal/secret/builtin-rules.go",
            "help": {
              "text": "Secret Slack Webhook\nSeverity: MEDIUM\nMatch:   slack: *******************************************************************************",
              "markdown": "**Secret Slack Webhook**\n| Severity | Match |\n| --- | --- |\n|MEDIUM|  slack: *******************************************************************************|"
            },
            "properties": {
              "precision": "very-high",
              "security-severity": "5.5",
              "tags": [
                "secret",
                "security",
                "MEDIUM"
              ]
            }
          }
        ],
        "version": "0.50.1"
      }
    }
  },
  "github": {
    "repo": "saritasa-nest/probot-tests",
    "headRef": "feature/add-checks-secrets",
    "actor": "darliiin",
    "eventName": "pull_request",
    "eventNumber": "216"
  }
}
```

Using [jinja2-action](https://github.com/cuchi/jinja2-action) and templates `slack-message-template.j2`, `pr-comment-secrets-template.j2` and `pr-comment-vulnerabilities-template.j2`
we are creating
1) message for Slack
2) comment for PR
3) summary for workflow


### If you want to test the jinja template locally:

1) install dependencies
```
sudo apt update
sudo apt install python3
```

2) prepare the following files:

* `.github/actions/security-audit/templates/slack-message-template.j2`

```
{% if data.file_names %}
*Exposed secrets found in github <https://github.com/{{data.github.repository}}/commit/{{data.github.sha}}|commit> by <https://github.com/{{data.github.actor}}|{{data.github.actor}}>*
*File list:*
{% for file in data.file_names %}
  <https://github.com/{{data.github.repository}}/blob/{{data.github.ref}}/{{file}}|{{file}}>
{% endfor %}
{% if data.github.event.name == 'pull_request' %}
  *Current <https://github.com/{{data.github.repository}}/pull/{{data.github.event.number}}|PR>*
{% endif %}
{% endif %}
```
* `tmp/variables-data.json`

```
{
  "file_names": [
    "one.key",
    "two.key"
  ],
  "github": {
    "repository": "saritasa-nest/probot-tests",
    "ref": "refs/pull/197/merge",
    "sha": "7b2a39630ceddf35e56852f3c3d3ad0dc9cd758d",
    "actor": "darliiin",
    "event": {
      "name": "pull_request",
      "number": "197"
    }
  }
}
```

* `script.py`
```
from jinja2 import Template
import json
with open("tmp/variables-data.json") as file:
    data = json.load(file)
with open(".github/actions/security-audit/templates/slack-message-template.j2") as file:
    template = Template(file.read())
with open("tmp/message.md", "w") as file:
    file.write(template.render(data=data))
```

and run the python script
```
python3 script.py
```
