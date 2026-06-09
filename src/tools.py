"""
OpenHuman AI Agent - Tools Module

Tools that the agent can use to interact with the environment,
execute commands, and perform various tasks.
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    output: Any = None
    error: str = ""
    metadata: Dict[str, Any] = None


class FileTool:
    """Tool for file operations."""
    
    @staticmethod
    def read(path: str, encoding: str = "utf-8") -> ToolResult:
        """Read file contents."""
        try:
            with open(path, 'r', encoding=encoding) as f:
                return ToolResult(
                    success=True,
                    output=f.read(),
                    metadata={"path": path, "size": os.path.getsize(path)}
                )
        except FileNotFoundError:
            return ToolResult(success=False, error=f"File not found: {path}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    @staticmethod
    def write(path: str, content: str, encoding: str = "utf-8") -> ToolResult:
        """Write content to file."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            return ToolResult(
                success=True,
                output={"path": path, "size": len(content)}
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    @staticmethod
    def append(path: str, content: str, encoding: str = "utf-8") -> ToolResult:
        """Append content to file."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'a', encoding=encoding) as f:
                f.write(content)
            return ToolResult(success=True, output={"path": path})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    @staticmethod
    def exists(path: str) -> bool:
        """Check if file exists."""
        return os.path.exists(path)
    
    @staticmethod
    def list_dir(path: str, pattern: str = "*") -> ToolResult:
        """List directory contents."""
        try:
            p = Path(path)
            if not p.exists():
                return ToolResult(success=False, error=f"Directory not found: {path}")
            
            items = [str(f.relative_to(p)) for f in p.glob(pattern)]
            return ToolResult(success=True, output=items)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    @staticmethod
    def create_dir(path: str) -> ToolResult:
        """Create directory."""
        try:
            os.makedirs(path, exist_ok=True)
            return ToolResult(success=True, output={"path": path})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    @staticmethod
    def delete(path: str, recursive: bool = False) -> ToolResult:
        """Delete file or directory."""
        try:
            p = Path(path)
            if p.is_file():
                p.unlink()
                return ToolResult(success=True, output={"path": path})
            elif p.is_dir():
                if recursive:
                    import shutil
                    shutil.rmtree(p)
                    return ToolResult(success=True, output={"path": path})
                else:
                    p.rmdir()
                    return ToolResult(success=True, output={"path": path})
            else:
                return ToolResult(success=False, error=f"Not found: {path}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GitTool:
    """Tool for Git operations."""
    
    @staticmethod
    def run(command: str, cwd: Optional[str] = None) -> ToolResult:
        """Run a git command."""
        try:
            result = subprocess.run(
                f"git {command}",
                shell=True,
                cwd=cwd or os.getcwd(),
                capture_output=True,
                text=True,
                timeout=60
            )
            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                metadata={"returncode": result.returncode}
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Git command timed out")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    @staticmethod
    def status(cwd: Optional[str] = None) -> ToolResult:
        """Get git status."""
        return GitTool.run("status --short", cwd)
    
    @staticmethod
    def diff(staged: bool = False, cwd: Optional[str] = None) -> ToolResult:
        """Get git diff."""
        cmd = "diff --staged" if staged else "diff"
        return GitTool.run(cmd, cwd)
    
    @staticmethod
    def log(limit: int = 10, cwd: Optional[str] = None) -> ToolResult:
        """Get git log."""
        return GitTool.run(f"log --oneline -{limit}", cwd)
    
    @staticmethod
    def branch(cwd: Optional[str] = None) -> ToolResult:
        """List git branches."""
        return GitTool.run("branch -v", cwd)
    
    @staticmethod
    def commit(message: str, cwd: Optional[str] = None) -> ToolResult:
        """Create a commit."""
        return GitTool.run(f'commit -m "{message}"', cwd)
    
    @staticmethod
    def push(force: bool = False, cwd: Optional[str] = None) -> ToolResult:
        """Push to remote."""
        cmd = "push --force" if force else "push"
        return GitTool.run(cmd, cwd)
    
    @staticmethod
    def pull(cwd: Optional[str] = None) -> ToolResult:
        """Pull from remote."""
        return GitTool.run("pull", cwd)
    
    @staticmethod
    def fetch(cwd: Optional[str] = None) -> ToolResult:
        """Fetch from remote."""
        return GitTool.run("fetch", cwd)


class ShellTool:
    """Tool for shell command execution."""
    
    @staticmethod
    def execute(
        command: str,
        cwd: Optional[str] = None,
        timeout: int = 300,
        env: Optional[Dict[str, str]] = None
    ) -> ToolResult:
        """Execute a shell command."""
        try:
            import shlex
            cmd_parts = shlex.split(command) if ' ' in command and not command.startswith('(') else [command]
            
            result = subprocess.run(
                command if '|' in command or '>' in command else cmd_parts,
                shell=any(c in command for c in ['|', '>', '(', ';', '$', '&&', '||']),
                cwd=cwd or os.getcwd(),
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, **(env or {})}
            )
            
            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                metadata={"returncode": result.returncode}
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error=f"Command timed out after {timeout} seconds")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    @staticmethod
    def which(command: str) -> Optional[str]:
        """Find command in PATH."""
        result = ShellTool.execute(f"which {command}")
        if result.success and result.output:
            return result.output.strip()
        return None


class SearchTool:
    """Tool for searching files and content."""
    
    @staticmethod
    def grep(pattern: str, path: str, recursive: bool = True, 
             file_pattern: str = "*") -> ToolResult:
        """Search for pattern in files."""
        try:
            cmd = f"grep -r" if recursive else "grep"
            result = subprocess.run(
                f"{cmd} -n '{pattern}' {path}/{file_pattern}" if recursive else f"{cmd} '{pattern}' {path}",
                shell=True,
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                timeout=60
            )
            return ToolResult(
                success=result.returncode in [0, 1],  # 1 = no match found
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else ""
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    @staticmethod
    def find(path: str, name_pattern: str = "*", 
             file_type: Optional[str] = None) -> ToolResult:
        """Find files by name pattern."""
        try:
            type_flag = ""
            if file_type == "file":
                type_flag = "-type f"
            elif file_type == "dir":
                type_flag = "-type d"
            
            result = subprocess.run(
                f"find {path} {type_flag} -name '{name_pattern}'",
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            return ToolResult(
                success=result.returncode == 0,
                output=[line for line in result.stdout.split('\n') if line]
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GHTool:
    """Tool for GitHub operations."""
    
    @staticmethod
    def run(command: str, token: Optional[str] = None) -> ToolResult:
        """Run a gh command."""
        try:
            token = token or os.environ.get("GITHUB_TOKEN", "")
            env = os.environ.copy()
            if token:
                env["GH_TOKEN"] = token
            
            result = subprocess.run(
                f"gh {command}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                env=env
            )
            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                metadata={"returncode": result.returncode}
            )
        except FileNotFoundError:
            return ToolResult(success=False, error="GitHub CLI (gh) not installed")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    @staticmethod
    def pr_list(state: str = "open", limit: int = 10) -> ToolResult:
        """List PRs."""
        return GHTool.run(f"pr list --state {state} --limit {limit}")
    
    @staticmethod
    def pr_view(pr_number: int, json_output: bool = True) -> ToolResult:
        """View a PR."""
        fmt = "--json number,title,body,state,url" if json_output else ""
        return GHTool.run(f"pr view {pr_number} {fmt}")
    
    @staticmethod
    def pr_checks(pr_number: int) -> ToolResult:
        """Get PR checks status."""
        return GHTool.run(f"pr checks {pr_number}")
    
    @staticmethod
    def pr_create(title: str, body: str, base: str = "main") -> ToolResult:
        """Create a PR."""
        return GHTool.run(f'pr create --title "{title}" --body "{body}" --base {base}')
    
    @staticmethod
    def issue_list(state: str = "open", limit: int = 10) -> ToolResult:
        """List issues."""
        return GHTool.run(f"issue list --state {state} --limit {limit}")


class Tools:
    """Collection of all available tools."""
    
    file = FileTool
    git = GitTool
    shell = ShellTool
    search = SearchTool
    gh = GHTool
    
    @classmethod
    def all(cls) -> List[str]:
        """List all tool names."""
        return [name for name in dir(cls) if not name.startswith('_') and name[0].islower()]