import os
import requests
from bs4 import BeautifulSoup
import argparse
import logging

ISSUES_DIR = os.path.join(os.environ["HOME"], ".local/share/phrack_issues")

# URL for Phrack's online archive
BASE_URL = "http://www.phrack.org/archives/tgz/"

# Ensure the local issues directory exists
os.makedirs(ISSUES_DIR, exist_ok=True)


def download_issues():
    """
    Downloads all available Phrack issues if they don't already exist locally.
    """
    # Fetch the issue list from Phrack website
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        print("Failed to fetch Phrack issue list.")
        return

    # Parse the page to find issue links
    soup = BeautifulSoup(response.content, "html.parser")
    issue_links = soup.find_all("a", href=True)

    issue_urls = [i for i in issue_links if i["href"].endswith("tar.gz")]

    for link in issue_links:
        issue_url = BASE_URL + link["href"]
        if not issue_url.endswith("tar.gz"):
            continue
        issue_filename = os.path.join(ISSUES_DIR, link["href"].split("/")[-1])

        # Check if the issue is already downloaded
        if os.path.exists(issue_filename):
            logging.info("Skipping {} (Already downloaded)".format(issue_filename))
            continue

        issue_response = requests.get(issue_url)
        if issue_response.status_code == 200:
            with open(issue_filename, "wb") as f:
                f.write(issue_response.content)
            logging.info("Saved {}".format(issue_filename))
        else:
            logging.error("Failed to download {}".format(issue_url))


def list_issues():
    """
    Lists all the downloaded issues.
    """
    issues = [f for f in os.listdir(ISSUES_DIR) if f.endswith(".txt")]
    if not issues:
        print("No issues found. Please download them first.")
        return

    print("\nAvailable Phrack Issues:")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")


def search_issues(keyword):
    """
    Searches for a keyword in both the title and content of the issues.
    """
    issues = [f for f in os.listdir(ISSUES_DIR) if f.endswith(".txt")]
    if not issues:
        print("No issues found. Please download them first.")
        return

    found_issues = []

    for issue in issues:
        issue_filepath = os.path.join(ISSUES_DIR, issue)

        # Check the title first
        with open(issue_filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().lower()
            if keyword.lower() in content:
                found_issues.append(issue)

    if found_issues:
        print(f"\nFound keyword '{keyword}' in the following issues:")
        for issue in found_issues:
            print(issue)
    else:
        print(f"No results found for '{keyword}'.")


def view_issue(issue_filename):
    """
    Displays the content of a Phrack issue in the terminal.
    """
    issue_filepath = os.path.join(ISSUES_DIR, issue_filename)
    if os.path.exists(issue_filepath):
        with open(issue_filepath, "r", encoding="utf-8", errors="ignore") as f:
            print(f.read())
    else:
        print(f"Error: {issue_filename} not found.")


def argParse():
    parser = None
    try:
        from rich_argparse import RichHelpFormatter
    except ModuleNotFoundError:
        parser = argparse.ArgumentParser(description="Interact with Phrack issues.")
    else:
        parser = argparse.ArgumentParser(
            description="Interact with Phrack issues.",
            formatter_class=RichHelpFormatter,
        )

    # Argument to download issues if needed
    parser.add_argument(
        "-d",
        "--download",
        action="store_true",
        help="Download all available Phrack issues.",
    )

    # Argument to list issues
    parser.add_argument(
        "-l", "--list", action="store_true", help="List all downloaded issues."
    )

    # Argument to search for a keyword
    parser.add_argument(
        "-s", "--search", type=str, help="Search for a keyword in titles and content."
    )

    # Argument to view a specific issue
    parser.add_argument(
        "-v", "--view", type=int, help="View the content of a specific issue by number."
    )

    # Parse arguments
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return None
    return args


def main():
    """
    Main function to handle command-line arguments using argparse.
    """
    args = argParse()
    if args == None:
        return 1

    # Download issues if requested
    if args.download:
        download_issues()

    # List issues if requested
    elif args.list:
        list_issues()

    # Search for a keyword if requested
    elif args.search:
        search_issues(args.search)

    # View a specific issue if requested
    elif args.view:
        issue_list = [f for f in os.listdir(ISSUES_DIR) if f.endswith(".txt")]
        try:
            issue_filename = issue_list[
                args.view - 1
            ]  # Convert from 1-indexed to 0-indexed
            view_issue(issue_filename)
        except IndexError:
            print(f"Invalid issue number {args.view}.")
    else:
        print("No action specified. Use --help for available options.")


if __name__ == "__main__":
    main()
