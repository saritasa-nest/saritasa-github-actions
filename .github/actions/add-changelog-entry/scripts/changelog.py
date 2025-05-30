import argparse
import sys
from datetime import datetime
import os


def changelog_add_entry(
    file_path: str,
    pr_number: int,
    pr_title: str,
    environment: str,
    repository: str,
    create_if_missing: bool,
) -> None:
    """
    Add a new entry to the changelog file with the specified PR number and title.

    Args:
        file_path (str): The path to the changelog file.
        pr_number (int): The pull request number to add to the changelog.
        pr_title (str): The pull request title or description.
        environment (str): The environment label to categorize the PR entry.
        repository (str): The GitHub repository in the format 'owner/repo'.
        create_if_missing (bool): Specify whether to create the file if it does not exist.
    """
    # Check if the file exists, and create it if necessary
    if not os.path.exists(file_path):
        if create_if_missing:
            with open(file_path, "w") as file:
                # Add the initial changelog title with a blank line
                file.write("# Changelog\n\n")
            print(f"File '{file_path}' created with initial # Changelog header.")
        else:
            print(f"Error: The file '{file_path}' does not exist.")
            sys.exit(1)

    current_date: str = datetime.now().strftime("%Y-%m-%d")

    # Define the new entry lines with PR number and PR title
    pr_line: str = (
        f"- [associated PR](https://github.com/{repository}/pull/{pr_number})\n"
    )
    new_entry_lines: list[str] = [
        pr_line,
        f"- {pr_title}\n",
    ]

    # Read the existing content of the file
    with open(file_path, "r") as file:
        lines: list[str] = file.readlines()

    # Check if the PR line already exists in the changelog
    if pr_line in lines:
        print(f"PR #{pr_number} is already listed in the changelog. Skipping addition.")
        return

    # Locate the # Changelog title and check for a current date section
    try:
        changelog_index: int = lines.index("# Changelog\n") + 1
    except ValueError:
        print("Error: The file does not have a '# Changelog' title.")
        sys.exit(1)

    # Ensure there's a blank line after # Changelog
    if lines[changelog_index] != "\n":
        lines.insert(changelog_index, "\n")
        changelog_index += 1

    # Check if today's date section already exists
    date_section_index = None
    for i, line in enumerate(lines[changelog_index:], start=changelog_index):
        if line.strip() == f"## {current_date}":
            date_section_index: int = i
            break

    if date_section_index is not None:
        # Check if the environment line is present after the date section
        env_index: int = date_section_index + 2
        if environment not in lines[env_index]:
            # Insert the environment label if it's missing, followed by a blank line
            lines.insert(env_index + 1, f"{environment}\n\n")
            env_index += 2  # Account for inserted environment and newline

        # Append the new entry lines after the environment section or at the end of the section
        insert_index: int = env_index + 2
        lines = lines[:insert_index] + new_entry_lines + lines[insert_index:]
    else:
        # Create a new date section with the current date, environment header, and blank lines
        new_section: list[str] = (
            [f"## {current_date}\n", "\n", f"{environment}\n", "\n"]
            + new_entry_lines
            + ["\n"]
        )
        lines = (
            lines[: changelog_index + 1] + new_section + lines[changelog_index + 1 :]
        )

    # Write the modified content back to the file
    with open(file_path, "w") as file:
        file.writelines(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update the changelog with a new PR entry."
    )
    parser.add_argument(
        "--repository",
        required=True,
        help="GitHub repository in the format 'owner/repo'",
    )
    parser.add_argument("--pr-number", required=True, help="The pull request number")
    parser.add_argument(
        "--pr-title", required=True, help="The pull request title or description"
    )
    parser.add_argument(
        "--environment",
        required=True,
        help="Environment label (e.g., dev, staging) to categorize the PR entry",
    )
    parser.add_argument(
        "--changelog-path", required=True, help="Path to the CHANGELOG.md file"
    )
    parser.add_argument(
        "--create-if-missing",
        choices=["enabled", "disabled"],
        default="disabled",
        help="Specify 'enabled' to create the CHANGELOG.md file if it does not exist, or 'disabled' to require its existence.",
    )

    args: argparse.Namespace = parser.parse_args()

    environment: str = f"[{args.environment}]"
    create_if_missing: bool = args.create_if_missing == "enabled"

    # Proceed with adding the entry to the changelog
    changelog_add_entry(
        file_path=args.changelog_path,
        pr_number=args.pr_number,
        pr_title=args.pr_title,
        environment=environment,
        repository=args.repository,
        create_if_missing=create_if_missing,
    )


if __name__ == "__main__":
    main()
