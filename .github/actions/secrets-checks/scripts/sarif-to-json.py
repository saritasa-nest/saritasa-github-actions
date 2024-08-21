import argparse
import json
import os
import re
from collections import defaultdict
from typing import Dict, NamedTuple


class BaseInfo(NamedTuple):
    """
        A named tuple for base information

        Named tuples assign meaning to each position in a tuple and allow for more readable, self-documenting code
        They add the ability to access fields by name instead of position index
    """
    location: Dict
    file_name: str
    start_line: int
    end_line: int

def asc_sort_dict_by_keys(obj: Dict[str, any]) -> Dict[str, any]:
    """
    Sorts the map by keys

    Args:
        obj (dict): Input dictionary
    Returns:
        dict: Output dictionary where elements are sorted by keys
    """
    return dict(sorted(obj.items()))

def extract_base_info(item: Dict[str, any]) -> BaseInfo:
    """
    Extracts base information from a scan result item

    Args:
        item (dict): An item from sarif file containing base information
    Returns:
        tuple: Contains the location, file name, start line, and end line
    """
    location = item['locations'][0]['physicalLocation']
    file_name = location['artifactLocation']['uri']
    start_line = location['region']['startLine']
    end_line = location['region']['endLine']
    return BaseInfo(location, file_name, start_line, end_line)

def convert_trivy_results_to_json(run: Dict[str, any]) -> Dict[str, any]:
    """
    Converts trivy analysis results into json format

    Args: run (dict): Data of the 'run' field from SARIF file
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
                },
                "results": [
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

    Returns: dict: A JSON object containing the conversion results
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
        "github": {
            "repo": "saritasa-nest/probot-tests",
            "headRefPush": "refs/pull/238/merge",
            "headRefPR": "darliiin-patch-1",
            "actor": "darliiin",
            "eventName": "pull_request",
            "eventNumber": "238",
            "commitSha": "10875e0749171a74ecc6f1de3579b213a846e0a9"
        }
    }
    """
    files = defaultdict(list)
    
    for item in run['results']:
        location, file_name, start_line, end_line = extract_base_info(item)
        
        # To specify the error type, need to convert the `severity` variable.
        # From: 
        #   Artifact: app/config.yaml
        #   Type: Secret GitHub Fine-grained personal access tokens
        #   Severity: CRITICAL
        #   Match:  name
        #   title: title
        #   token: ********************************************sdf
        #   token-2: *****
        # To: 
        #   CRITICAL
        severity = item['message']['text'].split('Severity: ')[1].split('\n')[0].strip()

        files[file_name].append({
            'name': file_name,
            'startLine': start_line,
            'endLine': end_line,
            'ruleId': item['ruleId'],
            'severity': severity,
        })

    result = {
        'trivy': {
            'totalFiles': len(files.keys()),
            'files': asc_sort_dict_by_keys(files),
            'details': run['tool'],
        },
    }

    return result

def convert_gitleaks_results_to_json(run: Dict[str, any]) -> Dict[str, any]:
    """
    Converts gitleaks analysis results into json format

    Args: run (dict): Data of the 'run' field from SARIF file
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

    Returns: dict: A JSON object containing the conversion results
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
    },

    """
    files = defaultdict(dict)

    for item in run['results']:
        location, file_name, start_line, end_line = extract_base_info(item)
        file_key = f"{start_line}-{end_line}"

        files[file_name].setdefault(file_key, {
            'name': file_name,
            'commits': [],
            'startLine': start_line,
            'endLine': end_line,
            'ruleId': item['ruleId'],
        })

        commitSha = item['partialFingerprints']['commitSha']
        files[file_name][file_key]['commits'].append(commitSha)

    result = {
        'gitleaks': {
            'totalFiles': len(files.keys()),
            'files': asc_sort_dict_by_keys(files),
            'uniqueFileNames': sorted([os.path.basename(file_name) for file_name in files.keys()]),
        },
    }

    return result

def main():
    """
    Convert sarif file with check results to json file

    Takes arguments, reads the contents of the specified sarif file,
    extracts the necessary information and converts it into the output json file
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='Path to the SARIF file to be converted')
    parser.add_argument('output_file', type=str, help='Path to the JSON file where the conversion result will be saved')
    parser.add_argument('check_type', type=str, choices=['trivy', 'gitleaks'], help='Check type (trivy or gitleaks)')

    args = parser.parse_args()

    with open(args.input_file, 'r', encoding='utf-8') as file:
        sarif_data = json.load(file)

    run = sarif_data['runs'][0]

    if not run['results']:
        return

    if args.check_type == 'trivy':
        result = convert_trivy_results_to_json(run)
    elif args.check_type == 'gitleaks':
        result = convert_gitleaks_results_to_json(run)

    with open(args.output_file, 'w', encoding='utf-8') as file:
        json.dump(result, file, indent=2)

if __name__ == '__main__':
    main()
