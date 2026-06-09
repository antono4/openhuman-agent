"""Git Workflow Skill - Git operations for development workflow."""

import subprocess
import re
from typing import Dict, List, Optional, Any


def run_git(command: str) -> Dict[str, Any]:
    """Execute a git command and return result."""
    try:
        result = subprocess.run(
            f"git {command}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip(),
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main(context: Dict = None) -> Dict[str, Any]:
    """
    Git Workflow skill - handles git operations.
    
    Context options:
        - action: "status", "diff", "commit", "push", "pull", "branch", "checkout", "log", "stash"
        - message: Commit message for commit action
        - branch: Branch name for branch/checkout actions
        - force: Force push flag
    """
    context = context or {}
    action = context.get("action", "status")
    
    if action == "status":
        return git_status()
    
    elif action == "diff":
        return git_diff(staged=context.get("staged", False))
    
    elif action == "commit":
        return git_commit(
            message=context.get("message", ""),
            amend=context.get("amend", False),
            all=context.get("all", False)
        )
    
    elif action == "push":
        return git_push(
            force=context.get("force", False),
            set_upstream=context.get("set_upstream", False)
        )
    
    elif action == "pull":
        return git_pull(rebase=context.get("rebase", True))
    
    elif action == "branch":
        return git_branch(list_all=context.get("list_all", True))
    
    elif action == "checkout":
        return git_checkout(
            branch=context.get("branch", ""),
            create=context.get("create", False)
        )
    
    elif action == "log":
        return git_log(limit=context.get("limit", 10))
    
    elif action == "stash":
        return git_stash(
            pop=context.get("pop", False),
            list_only=context.get("list_only", False)
        )
    
    elif action == "fetch":
        return git_fetch(all=context.get("all", True))
    
    else:
        return {"success": False, "error": f"Unknown action: {action}"}


def git_status() -> Dict[str, Any]:
    """Get git status."""
    return run_git("status --short")


def git_diff(staged: bool = False) -> Dict[str, Any]:
    """Get git diff."""
    cmd = "diff --staged" if staged else "diff"
    return run_git(cmd)


def git_commit(message: str, amend: bool = False, all: bool = False) -> Dict[str, Any]:
    """Create a git commit."""
    if not message:
        return {"success": False, "error": "Commit message is required"}
    
    # Sanitize message
    message_escaped = message.replace('"', '\\"')
    
    flags = ""
    if amend:
        flags += " --amend"
    if all:
        flags += " --all"
    
    result = run_git(f'commit{flags} -m "{message_escaped}"')
    
    if result["success"]:
        # Parse commit info
        output = result["output"]
        commit_match = re.search(r'\[[\w\s]+\s+([a-f0-9]+)\]', output)
        if commit_match:
            result["commit_hash"] = commit_match.group(1)
    
    return result


def git_push(force: bool = False, set_upstream: bool = False) -> Dict[str, Any]:
    """Push to remote."""
    flags = ""
    if force:
        flags += " --force-with-lease"  # Safer than --force
    if set_upstream:
        flags += " -u"
    
    result = run_git(f"push{flags}")
    return result


def git_pull(rebase: bool = True) -> Dict[str, Any]:
    """Pull from remote."""
    cmd = "pull --rebase" if rebase else "pull"
    return run_git(cmd)


def git_branch(list_all: bool = True) -> Dict[str, Any]:
    """List git branches."""
    cmd = "branch -a" if list_all else "branch"
    return run_git(cmd)


def git_checkout(branch: str, create: bool = False) -> Dict[str, Any]:
    """Checkout a branch."""
    if not branch:
        return {"success": False, "error": "Branch name is required"}
    
    cmd = f"checkout {'-b' if create else ''} {branch}".strip()
    return run_git(cmd)


def git_log(limit: int = 10) -> Dict[str, Any]:
    """Get git log."""
    return run_git(f"log --oneline --graph --decorate -{limit}")


def git_stash(pop: bool = False, list_only: bool = False) -> Dict[str, Any]:
    """Stash or unstash changes."""
    if list_only:
        return run_git("stash list")
    
    cmd = "stash pop" if pop else "stash"
    return run_git(cmd)


def git_fetch(all: bool = True) -> Dict[str, Any]:
    """Fetch from remotes."""
    cmd = "fetch --all" if all else "fetch"
    return run_git(cmd)


if __name__ == "__main__":
    import json
    result = main()
    print(json.dumps(result, indent=2))