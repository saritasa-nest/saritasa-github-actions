# pip install PyGithub
from github import GithubIntegration, Github, Auth
from changelog import changelog_add_entry
import argparse


def get_github_pr_with_token(token, repository, head, base):
    """
    This can be used whenever the PR information cannot be accessed using the
    Github context like: ${{ github.event.pull_request.title }}.
    For example when the script is not run on a Github Action
    """
    auth = Auth.Token(token)
    g = Github(auth=auth)
    repo = g.get_repo(repository)
    pulls = repo.get_pulls(state="open", base=base, head=head)
    if pulls.totalCount == 0:
        print("No PRs found for this HEAD branch. Exiting..")
        exit(1)
    if pulls.totalCount > 1:
        print("Found more than one PR with this HEAD, choosing the first one..")
    pr_number = pulls[0].number
    pr_title = pulls[0].title
    # To close connections after use
    g.close()
    return pr_number, pr_title


def get_github_pr_with_app(app_id, app_private_key, repository, head, base):
    """
    This can be used whenever the PR information cannot be accessed using the
    Github context like: ${{ github.event.pull_request.title }}.
    For example when the script is not run on a Github Action
    """
    auth = Auth.AppAuth(app_id, app_private_key)
    gi = GithubIntegration(auth=auth)
    installation = gi.get_installations()[0]
    g = installation.get_github_for_installation()
    repo = g.get_repo(repository)
    pulls = repo.get_pulls(state="open", base=base, head=head)
    if pulls.totalCount == 0:
        print("No PRs found for this HEAD branch. Exiting..")
        exit(1)
    if pulls.totalCount > 1:
        print("Found more than one PR with this HEAD, choosing the first one..")
    pr_number = pulls[0].number
    pr_title = pulls[0].title
    # To close connections after use
    g.close()
    return pr_number, pr_title


def main():
    parser = argparse.ArgumentParser(
        description="Update the changelog with a new PR entry."
    )
    parser.add_argument("--app-id", required=True, help="GitHub AppID")
    parser.add_argument(
        "--app-private-key", required=True, help="GitHub App private key"
    )
    parser.add_argument(
        "--repository",
        required=True,
        help="GitHub repository in the format 'owner/repo'",
    )
    parser.add_argument(
        "--head",
        required=True,
        help="The pull request head. The user/org must be pre appended: `org:ref-name`",
    )
    parser.add_argument("--base", required=True, help="The pull request base")
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

    args = parser.parse_args()

    environment = f"[{args.environment}]"
    create_if_missing = args.create_if_missing == "enabled"

    pr_number, pr_title = get_github_pr_with_app(
        args.app_id, args.app_private_key, args.repository, args.head, args.base
    )
    print(f"PR number: {pr_number}, PR title: {pr_title}")
    # Proceed with adding the entry to the changelog
    changelog_add_entry(
        args.changelog_path,
        pr_number,
        pr_title,
        environment,
        args.repository,
        create_if_missing,
    )


if __name__ == "__main__":
    main()
