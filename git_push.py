#!/usr/bin/env python3
import subprocess
import sys

def run_git_command(command):
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False

def main():
    # Get commit message from command-line argument if provided
    if len(sys.argv) > 1:
        commit_message = sys.argv[1]
    else:
        commit_message = "new"

    # Git add
    if not run_git_command(["git", "add", "."]):
        sys.exit(1)

    # Git commit
    if not run_git_command(["git", "commit", "-m", commit_message]):
        sys.exit(1)

    # Git push
    if not run_git_command(["git", "push"]):
        sys.exit(1)

    print("Git add, commit, and push completed successfully.")

if __name__ == "__main__":
    main()
