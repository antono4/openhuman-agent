"""GitHub PR Manager Skill - Manage GitHub pull requests."""

import json
import subprocess
import re
from typing import Dict, List, Optional, Any


def run_gh(command: str) -> Dict[str, Any]:
    """Execute a gh command and return result."""
    try:
        result = subprocess.run(
            f"gh {command}",
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
    GitHub PR Manager skill - handles PR operations.
    
    Context options:
        - action: "list", "view", "create", "merge", "close"
        - pr_number: PR number for view/merge/close actions
        - title: PR title for create action
        - body: PR description for create action
        - base: Target branch (default: main)
    """
    context = context or {}
    action = context.get("action", "list")
    
    if action == "list":
        return list_prs(
            state=context.get("state", "open"),
            limit=context.get("limit", 10)
        )
    
    elif action == "view":
        return view_pr(context.get("pr_number"))
    
    elif action == "create":
        return create_pr(
            title=context.get("title", ""),
            body=context.get("body", ""),
            base=context.get("base", "main")
        )
    
    elif action == "checks":
        return get_pr_checks(context.get("pr_number"))
    
    elif action == "merge":
        return merge_pr(
            pr_number=context.get("pr_number"),
            squash=context.get("squash", False),
            delete_branch=context.get("delete_branch", True)
        )
    
    elif action == "close":
        return close_pr(context.get("pr_number"))
    
    else:
        return {"success": False, "error": f"Unknown action: {action}"}


def list_prs(state: str = "open", limit: int = 10) -> Dict[str, Any]:
    """List pull requests."""
    result = run_gh(f"pr list --state {state} --limit {limit} --json number,title,state,url,author")
    
    if result["success"]:
        try:
            prs = json.loads(result["output"])
            return {"success": True, "prs": prs}
        except json.JSONDecodeError:
            return {"success": True, "prs": result["output"].split("\n")}
    
    return result


def view_pr(pr_number: int) -> Dict[str, Any]:
    """View a specific pull request."""
    result = run_gh(
        f"pr view {pr_number} --json number,title,body,state,url,author,headRefName,baseRefName,mergeable,statusCheckRollup"
    )
    
    if result["success"]:
        try:
            pr_data = json.loads(result["output"])
            return {"success": True, "pr": pr_data}
        except json.JSONDecodeError:
            return {"success": True, "pr": result["output"]}
    
    return result


def create_pr(title: str, body: str, base: str = "main") -> Dict[str, Any]:
    """Create a new pull request."""
    if not title:
        return {"success": False, "error": "PR title is required"}
    
    # Escape quotes in title and body
    title_escaped = title.replace('"', '\\"')
    body_escaped = body.replace('"', '\\"') if body else ""
    
    result = run_gh(f'pr create --title "{title_escaped}" --body "{body_escaped}" --base {base}')
    
    if result["success"]:
        # Extract PR URL from output
        url_match = re.search(r'https://github\.com/[\w-]+/[\w-]+/pull/\d+', result["output"])
        if url_match:
            return {"success": True, "url": url_match.group(0)}
        return {"success": True, "output": result["output"]}
    
    return result


def get_pr_checks(pr_number: int) -> Dict[str, Any]:
    """Get status checks for a PR."""
    result = run_gh(f"pr checks {pr_number} --json name,state,conclusion")
    
    if result["success"]:
        try:
            checks = json.loads(result["output"])
            return {"success": True, "checks": checks}
        except json.JSONDecodeError:
            return {"success": True, "checks": result["output"].split("\n")}
    
    return result


def merge_pr(pr_number: int, squash: bool = False, delete_branch: bool = True) -> Dict[str, Any]:
    """Merge a pull request."""
    squash_flag = "--squash" if squash else ""
    delete_flag = "--delete-branch" if delete_branch else ""
    
    result = run_gh(f"pr merge {pr_number} {squash_flag} {delete_flag} --admin --auto")
    
    return result


def close_pr(pr_number: int) -> Dict[str, Any]:
    """Close a pull request."""
    result = run_gh(f"pr close {pr_number} --delete-branch")
    return result


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))