"""Example: Safe Read the Docs API request.

This script demonstrates fetching the Read the Docs project API using a
token read from an environment variable (do NOT hardcode tokens).
"""
import os
import sys
import requests


def main():
    URL = "https://app.readthedocs.org/api/v3/projects/pip/"
    token = os.environ.get("READTHEDOCS_TOKEN")
    if not token:
        print("ERROR: set READTHEDOCS_TOKEN in environment before running.")
        sys.exit(2)

    headers = {"Authorization": f"token {token}"}
    try:
        resp = requests.get(URL, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print("Request failed:", exc)
        sys.exit(1)

    print(resp.json())


if __name__ == "__main__":
    main()
