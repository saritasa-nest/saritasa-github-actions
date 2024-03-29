Gitleaks is a tool for detecting and preventing hardcoded secrets(i.e. ssh pem keys, our files ending with .secrets).

We use our own gitleaks configuration gitleaks.toml, it is located at the root of the repository, automatically detected and used by gitleaks-action.

To use gitleaks in an organization, we need `GITLEAKS_LICENSE`, get here https://gitleaks.io/products.html

1) go to fill out the Google form
2) paste devops@saritasa.com into the email field
3) wait for the key, add it to GitHub at the organization level https://github.com/organizations/saritasa-nest/settings/secrets/actions

After receiving the `gitleaks-results.sarif` file, a json file is created with the names of the files with leaked secrets and github variables.

An example of what the generated `variables.json` looks like
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

Next, we pass the generated `variables.json` file and template `.github/actions/checks-secrets-gitleaks/templates/slack-message-template.j2` to the `jinja2-action` to generate `slack_message.md`

**So get a ready message to send to Slack.**

If you want to test the jinja template locally:

1) install dependencies
```
sudo apt update

sudo apt install python3
```

2) prepare the following files:

* `.github/actions/checks-secrets-gitleaks/templates/slack-message-template.j2`

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
* `/tmp/variables-data.json`

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
with open("/tmp/variables-data.json") as file:
    data = json.load(file)
with open(".github/actions/checks-secrets-gitleaks/templates/slack-message-template.j2") as file:
    template = Template(file.read())
with open("/tmp/message.md", "w") as file:
    file.write(template.render(data=data))
```

and run the python script 
```
python3 script.py
```