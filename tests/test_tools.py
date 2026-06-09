"""Tests for the OpenHuman AI Agent tools."""

import pytest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools import FileTool, GitTool, ShellTool, SearchTool, ToolResult


class TestFileTool:
    """Tests for FileTool."""
    
    def test_file_read(self, tmp_path):
        """Test reading a file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        result = FileTool.read(str(test_file))
        assert result.success is True
        assert result.output == "Hello, World!"
    
    def test_file_read_not_found(self):
        """Test reading a non-existent file."""
        result = FileTool.read("/nonexistent/file.txt")
        assert result.success is False
        assert "not found" in result.error.lower()
    
    def test_file_write(self, tmp_path):
        """Test writing to a file."""
        test_file = tmp_path / "output.txt"
        
        result = FileTool.write(str(test_file), "Test content")
        assert result.success is True
        assert test_file.read_text() == "Test content"
    
    def test_file_append(self, tmp_path):
        """Test appending to a file."""
        test_file = tmp_path / "append.txt"
        test_file.write_text("Initial")
        
        result = FileTool.append(str(test_file), " and appended")
        assert result.success is True
        assert test_file.read_text() == "Initial and appended"
    
    def test_file_exists(self, tmp_path):
        """Test checking file existence."""
        test_file = tmp_path / "exists.txt"
        test_file.write_text("test")
        
        assert FileTool.exists(str(test_file)) is True
        assert FileTool.exists("/nonexistent.txt") is False
    
    def test_file_list_dir(self, tmp_path):
        """Test listing directory contents."""
        (tmp_path / "file1.txt").write_text("1")
        (tmp_path / "file2.txt").write_text("2")
        (tmp_path / "subdir").mkdir()
        
        result = FileTool.list_dir(str(tmp_path))
        assert result.success is True
        assert "file1.txt" in result.output
        assert "file2.txt" in result.output
    
    def test_file_create_dir(self, tmp_path):
        """Test creating a directory."""
        new_dir = tmp_path / "new" / "nested" / "dir"
        
        result = FileTool.create_dir(str(new_dir))
        assert result.success is True
        assert new_dir.exists()
    
    def test_file_delete(self, tmp_path):
        """Test deleting a file."""
        test_file = tmp_path / "delete_me.txt"
        test_file.write_text("delete")
        
        result = FileTool.delete(str(test_file))
        assert result.success is True
        assert not test_file.exists()
    
    def test_file_delete_recursive(self, tmp_path):
        """Test deleting a directory recursively."""
        test_dir = tmp_path / "delete_dir"
        test_dir.mkdir()
        (test_dir / "file.txt").write_text("delete")
        
        result = FileTool.delete(str(test_dir), recursive=True)
        assert result.success is True
        assert not test_dir.exists()


class TestGitTool:
    """Tests for GitTool."""
    
    def test_git_status(self):
        """Test git status command."""
        result = GitTool.status()
        assert result is not None
        # Result should have success or error, not both
        assert result.success is not None
    
    def test_git_branch(self):
        """Test git branch command."""
        result = GitTool.branch()
        assert result is not None
        assert hasattr(result, "success")


class TestShellTool:
    """Tests for ShellTool."""
    
    def test_shell_execute_success(self):
        """Test successful shell execution."""
        result = ShellTool.execute("echo 'Hello'")
        assert result.success is True
        assert "Hello" in result.output
    
    def test_shell_execute_failure(self):
        """Test failed shell execution."""
        result = ShellTool.execute("ls /nonexistent_directory_12345")
        assert result.success is False
        assert result.metadata is not None
        assert result.metadata.get("returncode") != 0
    
    def test_shell_execute_with_cwd(self, tmp_path):
        """Test shell execution with working directory."""
        result = ShellTool.execute("pwd", cwd=str(tmp_path))
        assert result.success is True
        assert str(tmp_path) in result.output
    
    def test_shell_which(self):
        """Test finding a command in PATH."""
        result = ShellTool.which("python3")
        # python3 should be found
        assert result is not None


class TestSearchTool:
    """Tests for SearchTool."""
    
    def test_search_find(self, tmp_path):
        """Test finding files."""
        (tmp_path / "test1.txt").write_text("1")
        (tmp_path / "test2.txt").write_text("2")
        (tmp_path / "other.log").write_text("3")
        
        result = SearchTool.find(str(tmp_path), "*.txt")
        assert result.success is True
        assert len(result.output) >= 2


class TestToolResult:
    """Tests for ToolResult."""
    
    def test_tool_result_success(self):
        """Test successful tool result."""
        result = ToolResult(
            success=True,
            output="test output",
            metadata={"size": 100}
        )
        assert result.success is True
        assert result.output == "test output"
        assert result.metadata["size"] == 100
    
    def test_tool_result_failure(self):
        """Test failed tool result."""
        result = ToolResult(
            success=False,
            error="Something went wrong"
        )
        assert result.success is False
        assert result.error == "Something went wrong"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])