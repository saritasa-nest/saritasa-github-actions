# SARIF to JSON Conversion Scripts

This directory contains scripts for converting SARIF security scan results into compact JSON representations for further processing or reporting.

## Functions Overview

### convert_gitleaks_results_to_json

Converts Gitleaks SARIF results into a compact JSON format.

- **Input:** SARIF `run` dictionary from Gitleaks output.
```
{
  "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "gitleaks",
          "semanticVersion": "v8.0.0",
          "rules": [
            {
              "id": "secrets",
              "name": "all secrets files",
              "shortDescription": {
                "text": ".*"
              }
            },
            {
              "id": "*.pem",
              "name": "all .pem files",
              "shortDescription": {
                "text": "(?s).+"
              }
            },
            {
              "id": "*.key",
              "name": "all .key files",
              "shortDescription": {
                "text": "(?s).+"
              }
            }
          ]
        }
      },
      "results": [
        {
          "message": {
            "text": "github-pat has detected secret for file app/config.yaml at commit 0988ecc87aafa2677c6669fad3f03f15f0eb83f4."
          },
          "ruleId": "github-pat",
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "app/config.yaml"
                },
                "region": {
                  "startLine": 7,
                  "startColumn": 10,
                  "endLine": 7,
                  "endColumn": 49,
                  "snippet": {
                    "text": "REDACTED"
                  }
                }
              }
            }
          ],
          "partialFingerprints": {
            "commitSha": "0988ecc87aafa2677c6669fad3f03f15f0eb83f4",
            "email": "117597862+darliiin@users.noreply.github.com",
            "author": "Dariya Nalimova",
            "date": "2024-07-05T06:48:12Z",
            "commitMessage": "Update config.yaml"
          }
        }
      ]
    }
  ]
}
```

- **Output:** JSON object containing the conversion results
```
"gitleaks": {
  "totalFiles": 1,
  "files": {
    "app/config.yaml": {
      "7-7": {
        "name": "app/config.yaml",
        "commits": [
          "0988ecc87aafa2677c6669fad3f03f15f0eb83f4"
        ],
        "startLine": 7,
        "endLine": 7,
        "ruleId": "github-pat"
      }
    }
  },
  "uniqueFileNames": [
    "config.yaml"
  ]
}
```

### convert_trivy_results_to_json

Converts Trivy SARIF results into a compact JSON format.

- **Input:** SARIF `run` dictionary from Trivy output.

```
{
  "version": "2.1.0",
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "fullName": "Trivy Vulnerability Scanner",
          "informationUri": "https://github.com/aquasecurity/trivy",
          "name": "Trivy",
          "rules": [
            {
              "id": "CVE-2024-4067",
              "name": "LanguageSpecificPackageVulnerability",
              "shortDescription": {
                "text": "micromatch: vulnerable to Regular Expression Denial of Service"
              },
              "fullDescription": {
                "text": "The NPM package `micromatch` prior to 4.0.8 is vulnerable to Regular Expression Denial of Service (ReDoS). The vulnerability occurs in `micromatch.braces()` in `index.js` because the pattern `.*` will greedily match anything. By passing a malicious payload, the pattern matching will keep backtracking to the input while it doesn't find the closing bracket. As the input size increases, the consumption time will also increase until it causes the application to hang or slow down. There was a merged fix but further testing shows the issue persists. This issue should be mitigated by using a safe pattern that won't start backtracking the regular expression due to greedy matching. This issue was fixed in version 4.0.8."
              },
              "defaultConfiguration": {
                "level": "warning"
              },
              "helpUri": "https://avd.aquasec.com/nvd/cve-2024-4067",
              "help": {
                "text": "Vulnerability CVE-2024-4067\nSeverity: MEDIUM\nPackage: micromatch\nFixed Version: 4.0.8\nLink: [CVE-2024-4067](https://avd.aquasec.com/nvd/cve-2024-4067)\nThe NPM package `micromatch` prior to 4.0.8 is vulnerable to Regular Expression Denial of Service (ReDoS). The vulnerability occurs in `micromatch.braces()` in `index.js` because the pattern `.*` will greedily match anything. By passing a malicious payload, the pattern matching will keep backtracking to the input while it doesn't find the closing bracket. As the input size increases, the consumption time will also increase until it causes the application to hang or slow down. There was a merged fix but further testing shows the issue persists. This issue should be mitigated by using a safe pattern that won't start backtracking the regular expression due to greedy matching. This issue was fixed in version 4.0.8.",
                "markdown": "**Vulnerability CVE-2024-4067**\n| Severity | Package | Fixed Version | Link |\n| --- | --- | --- | --- |\n|MEDIUM|micromatch|4.0.8|[CVE-2024-4067](https://avd.aquasec.com/nvd/cve-2024-4067)|\n\nThe NPM package `micromatch` prior to 4.0.8 is vulnerable to Regular Expression Denial of Service (ReDoS). The vulnerability occurs in `micromatch.braces()` in `index.js` because the pattern `.*` will greedily match anything. By passing a malicious payload, the pattern matching will keep backtracking to the input while it doesn't find the closing bracket. As the input size increases, the consumption time will also increase until it causes the application to hang or slow down. There was a merged fix but further testing shows the issue persists. This issue should be mitigated by using a safe pattern that won't start backtracking the regular expression due to greedy matching. This issue was fixed in version 4.0.8."
              },
              "properties": {
                "precision": "very-high",
                "security-severity": "5.3",
                "tags": [
                  "vulnerability",
                  "security",
                  "MEDIUM"
                ]
              }
            },
            {
              "id": "github-pat",
              "name": "Secret",
              "shortDescription": {
                "text": "GitHub Personal Access Token"
              },
              "fullDescription": {
                "text": "  token: ****************************************"
              },
              "defaultConfiguration": {
                "level": "error"
              },
              "helpUri": "https://github.com/aquasecurity/trivy/blob/main/pkg/fanal/secret/builtin-rules.go",
              "help": {
                "text": "Secret GitHub Personal Access Token\nSeverity: CRITICAL\nMatch:   token: ****************************************",
                "markdown": "**Secret GitHub Personal Access Token**\n| Severity | Match |\n| --- | --- |\n|CRITICAL|  token: ****************************************|"
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
            }
          ],
          "version": "0.51.2"
        }
      },
      "results": [
        {
          "ruleId": "CVE-2024-4067",
          "ruleIndex": 0,
          "level": "warning",
          "message": {
            "text": "Package: micromatch\nInstalled Version: 3.1.10\nVulnerability CVE-2024-4067\nSeverity: MEDIUM\nFixed Version: 4.0.8\nLink: [CVE-2024-4067](https://avd.aquasec.com/nvd/cve-2024-4067)"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "package-lock.json",
                  "uriBaseId": "ROOTPATH"
                },
                "region": {
                  "startLine": 1301,
                  "startColumn": 1,
                  "endLine": 1324,
                  "endColumn": 1
                }
              },
              "message": {
                "text": "package-lock.json: micromatch@3.1.10"
              }
            }
          ]
        },
        {
          "ruleId": "github-pat",
          "ruleIndex": 0,
          "level": "error",
          "message": {
            "text": "Artifact: app/config.yaml\nType: \nSecret GitHub Personal Access Token\nSeverity: CRITICAL\nMatch:   token: ****************************************"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "app/config.yaml",
                  "uriBaseId": "ROOTPATH"
                },
                "region": {
                  "startLine": 7,
                  "startColumn": 1,
                  "endLine": 7,
                  "endColumn": 1
                }
              },
              "message": {
                "text": "app/config.yaml"
              }
            }
          ]
        }
      ],
      "columnKind": "utf16CodeUnits",
      "originalUriBaseIds": {
        "ROOTPATH": {
          "uri": "file:///github/workspace/"
        }
      }
    }
  ]
}   
```

- **Output:** JSON object with detected vulnerabilities and secrets.

```
{
  "trivy": {
    "totalFiles": 1,
    "files": {
      "app/config.yaml": [
        {
          "name": "app/config.yaml",
          "startLine": 7,
          "endLine": 7,
          "ruleId": "github-pat",
          "severity": "CRITICAL"
        },
      ]
    },
    "details": {
      "driver": {
        "fullName": "Trivy Vulnerability Scanner",
        "informationUri": "https://github.com/aquasecurity/trivy",
        "name": "Trivy",
        "rules": [
          {
            "id": "github-pat",
            "name": "Secret",
            "shortDescription": {
              "text": "GitHub Personal Access Token"
            },
            "fullDescription": {
              "text": "  token: ****************************************"
            },
            "defaultConfiguration": {
              "level": "error"
            },
            "helpUri": "https://github.com/aquasecurity/trivy/blob/main/pkg/fanal/secret/builtin-rules.go",
            "help": {
              "text": "Secret GitHub Personal Access Token\nSeverity: CRITICAL\nMatch:   token: ****************************************",
              "markdown": "**Secret GitHub Personal Access Token**\n| Severity | Match |\n| --- | --- |\n|CRITICAL|  token: ****************************************|"
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
        ],
        "version": "0.51.2"
      }
    }
  },
  "vulnerabilities": {
    "totalFiles": 1,
    "files": {
      "package-lock.json": [
        {
          "name": "package-lock.json",
          "startLine": 1301,
          "endLine": 1324,
          "ruleId": "CVE-2",
          "severity": "MEDIUM",
          "package": "micromatch",
          "description": "The NPM package `micromatch` prior to 4.0.8 is vulnerable to ReDoS",
          "fixedVersion": "4.0.8"
        }
      ]
    },
    "details": {
      "driver": {
        "fullName": "Trivy Vulnerability Scanner",
        "informationUri": "https://github.com/aquasecurity/trivy",
        "name": "Trivy",
        "rules": [
          {
            "id": "CVE-2",
            "name": "LanguageSpecificPackageVulnerability",
            "shortDescription": {
              "text": "micromatch: vulnerable to Regular Expression Denial of Service"
            },
            "fullDescription": {
              "text": "The NPM package `micromatch` prior to 4.0.8 is vulnerable to ReDoS."
            },
            "defaultConfiguration": {
              "level": "warning"
            },
            "helpUri": "https://avd.aquasec.com/nvd/cve-2",
            "help": {
              "text": "Vulnerability CVE-2\nSeverity: MEDIUM\nPackage: micromatch\nFixed Version: 4.0.8\nLink: [CVE-2](https://avd.aquasec.com/nvd/cve-2)\nThe NPM package `micromatch` prior to 4.0.8 is vulnerable to  ReDoS.",
              "markdown": "**Vulnerability CVE-2**\n| Severity | Package | Fixed Version | Link |\n| --- | --- | --- | --- |\n|MEDIUM|micromatch|4.0.8|[CVE-2](https://avd.aquasec.com/nvd/cve-2)|\n\nThe NPM package `micromatch` prior to 4.0.8 is vulnerable to ReDoS."
            },
            "properties": {
              "precision": "very-high",
              "security-severity": "5.3",
              "tags": [
                "vulnerability",
                "security",
                "MEDIUM"
              ]
            }
          }
        ],
        "version": "0.56.2"
      }
    }
  },
  "github": {
    "repo": "saritasa-nest/probot-tests",
    "pushBranch": "refs/pull/238/merge",
    "pullRequestBranch": "darliiin-patch-1",
    "actor": "darliiin",
    "eventName": "pull_request",
    "eventNumber": "238",
    "commitSha": "10875e0749171a74ecc6f1de3579b213a846e0a9"
  }
}
```
