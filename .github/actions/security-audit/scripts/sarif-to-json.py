import argparse
import json
import os
from collections import defaultdict
from typing import NamedTuple

class BaseInfo(NamedTuple):
    """
    Base information of the scan result items.
    """
    location: dict
    file_name: str
    start_line: int
    end_line: int

def asc_sort_dict_by_keys(obj: dict[str, any]) -> dict[str, any]:
    """
    Sorts a dictionary by keys in ascending order

    Args:
        obj (dict): Input dictionary
    Returns:
        dict: Output dictionary where elements are sorted by keys
    """
    return dict(sorted(obj.items()))

def extract_base_info(item: dict[str, any]) -> BaseInfo:
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

def convert_gitleaks_results_to_json(run: dict[str, any]) -> dict[str, any]:
    """
    Converts gitleaks analysis results into json format

    Args: 
        run (dict): Data of the 'run' field from SARIF file
    Returns: 
        dict: A JSON object containing the conversion results
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

    return {
        'gitleaks': {
            'totalFiles': len(files.keys()),
            'files': asc_sort_dict_by_keys(files),
            'uniqueFileNames': sorted([os.path.basename(file_name) for file_name in files.keys()]),
        },
    }

def convert_trivy_results_to_json(run: dict[str, any]) -> dict[str, any]:
    """
    This function processes SARIF scan results and returns a dictionary 
    containing unencrypted secrets and vulnerabilities found in the scanned files.

    Args: 
        run (dict): Data of the 'run' field from SARIF file
    Returns: 
        dict: A JSON object containing the conversion results
            {
                'vulnerabilities': {...},  # Vulnerabilities results
                'trivy': {...},            # Secrets results
            }
    """
    secrets = defaultdict(list)
    vulnerability_rules = defaultdict(list)
    vulnerabilities = defaultdict(list)

    # Preprocess rules to extract vulnerability descriptions.
    # This allows us to later supplement scan results by matching rule ID → description.
    for rule in run['tool']['driver']['rules']:
        rule_id = rule['id']
        if 'vulnerability' in rule['properties']['tags']:
            vulnerability_rules[rule_id] = {
                'description': rule['fullDescription']['text'].rstrip(),
            }

    # Extract the following data from scan results:
    #   file name, start and end line numbers (to generate precise links to the content), and severity level.
    # For vulnerabilities, we additionally extract 
    #   package name, installed and fixed versions, rule description.
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
        default = {
            'name': file_name,
            'startLine': start_line,
            'endLine': end_line,
            'ruleId': item['ruleId'],
            'severity': severity,
        }
        rule = vulnerability_rules.get(item['ruleId'])
        if rule:
            text = item['message']['text']
            vulnerabilities[file_name].append({
                'package': text.split('Package: ')[1].split('\n')[0].strip(),
                'installedVersion': text.split('Installed Version: ')[1].split('\n')[0].strip(),
                'fixedVersion':  text.split('Fixed Version: ')[1].split('\n')[0].strip(),
                'description': rule.get('description'),
                **default,
            })
        else:
            secrets[file_name].append(default.copy())
    return {
        'vulnerabilities': {
            'totalFiles': len(vulnerabilities.keys()),
            'files': asc_sort_dict_by_keys(vulnerabilities),
            'details': run['tool'],
        },
        'trivy': {
            'totalFiles': len(secrets.keys()),
            'files': asc_sort_dict_by_keys(secrets),
            'details': run['tool'],
        },
    }

def main():
    """
    Convert sarif file with check results to json file

    Takes arguments, reads the contents of the specified sarif file,
    extracts the necessary information and converts it into the output json file
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='Path to the SARIF file to be converted')
    parser.add_argument('output_file', type=str, help='Path to the JSON file where the conversion result will be saved')
    parser.add_argument('check_type', type=str, choices=['trivy', 'gitleaks'], help='Check type (trivy, gitleaks)')

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
