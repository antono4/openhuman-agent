"""Tests for the OpenHuman AI Agent skill loader."""

import pytest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from skill_loader import SkillLoader, Skill, SkillMetadata


class TestSkillMetadata:
    """Tests for SkillMetadata."""
    
    def test_from_dict(self):
        """Test creating metadata from dict."""
        data = {
            "name": "test-skill",
            "description": "A test skill",
            "category": "development",
            "version": "1.0.0",
            "author": "Test Author",
            "tags": ["test", "example"],
            "entry_point": "main",
            "requires": ["git"]
        }
        
        metadata = SkillMetadata.from_dict(data)
        assert metadata.name == "test-skill"
        assert metadata.description == "A test skill"
        assert metadata.category == "development"
        assert metadata.version == "1.0.0"
        assert metadata.tags == ["test", "example"]
        assert metadata.entry_point == "main"
    
    def test_from_dict_defaults(self):
        """Test default values when creating from dict."""
        data = {"name": "minimal-skill"}
        
        metadata = SkillMetadata.from_dict(data)
        assert metadata.name == "minimal-skill"
        assert metadata.description == ""
        assert metadata.category == "general"
        assert metadata.version == "1.0.0"


class TestSkill:
    """Tests for Skill."""
    
    def test_skill_creation(self):
        """Test creating a skill."""
        skill = Skill(
            name="test-skill",
            description="A test skill",
            category="development"
        )
        assert skill.name == "test-skill"
        assert skill.description == "A test skill"
        assert skill.category == "development"
    
    def test_skill_execute_without_callable(self):
        """Test executing a skill without callable raises error."""
        skill = Skill(
            name="no-callable",
            description="No callable function"
        )
        
        with pytest.raises(NotImplementedError):
            skill.execute()


class TestSkillLoader:
    """Tests for SkillLoader."""
    
    def test_init_empty_directory(self, tmp_path):
        """Test initialization with empty skills directory."""
        loader = SkillLoader(str(tmp_path / "nonexistent"))
        assert loader.list_skills() == []
    
    def test_load_skill_from_directory(self, tmp_path):
        """Test loading a skill from a directory."""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        
        # Create skill.json
        metadata = {
            "name": "test-skill",
            "description": "A test skill",
            "category": "development",
            "version": "1.0.0",
            "entry_point": "main"
        }
        with open(skill_dir / "skill.json", "w") as f:
            json.dump(metadata, f)
        
        # Create skill.py
        with open(skill_dir / "skill.py", "w") as f:
            f.write("""
def main(context=None):
    return {"status": "success", "skill": "test-skill"}
""")
        
        loader = SkillLoader(str(tmp_path))
        skills = loader.list_skills()
        
        assert "test-skill" in skills
        
        skill = loader.get_skill("test-skill")
        assert skill is not None
        assert skill.name == "test-skill"
        assert skill.description == "A test skill"
    
    def test_load_skill_metadata_only(self, tmp_path):
        """Test loading a skill with only metadata (no Python)."""
        skill_dir = tmp_path / "metadata-only"
        skill_dir.mkdir()
        
        metadata = {
            "name": "metadata-only",
            "description": "Skill without Python module"
        }
        with open(skill_dir / "skill.json", "w") as f:
            json.dump(metadata, f)
        
        loader = SkillLoader(str(tmp_path))
        skill = loader.get_skill("metadata-only")
        
        assert skill is not None
        assert skill.name == "metadata-only"
        assert skill.callable is None
    
    def test_list_skills_filtered_by_category(self, tmp_path):
        """Test listing skills filtered by category."""
        # Create skills in different categories
        for name, category in [("skill1", "dev"), ("skill2", "dev"), ("skill3", "ops")]:
            skill_dir = tmp_path / name
            skill_dir.mkdir()
            
            metadata = {
                "name": name,
                "description": f"{name} description",
                "category": category
            }
            with open(skill_dir / "skill.json", "w") as f:
                json.dump(metadata, f)
        
        loader = SkillLoader(str(tmp_path))
        
        dev_skills = loader.list_skills(category="dev")
        assert len(dev_skills) == 2
        assert "skill1" in dev_skills
        assert "skill2" in dev_skills
    
    def test_list_categories(self, tmp_path):
        """Test listing all categories."""
        for name, category in [("s1", "dev"), ("s2", "dev"), ("s3", "ops")]:
            skill_dir = tmp_path / name
            skill_dir.mkdir()
            
            metadata = {"name": name, "category": category}
            with open(skill_dir / "skill.json", "w") as f:
                json.dump(metadata, f)
        
        loader = SkillLoader(str(tmp_path))
        categories = loader.list_categories()
        
        assert "dev" in categories
        assert "ops" in categories
    
    def test_search_skills_by_name(self, tmp_path):
        """Test searching skills by name."""
        skill_dir = tmp_path / "github-pr"
        skill_dir.mkdir()
        
        metadata = {
            "name": "github-pr",
            "description": "GitHub PR management"
        }
        with open(skill_dir / "skill.json", "w") as f:
            json.dump(metadata, f)
        
        loader = SkillLoader(str(tmp_path))
        results = loader.search_skills("github")
        
        assert len(results) == 1
        assert results[0].name == "github-pr"
    
    def test_search_skills_by_description(self, tmp_path):
        """Test searching skills by description."""
        skill_dir = tmp_path / "git-workflow"
        skill_dir.mkdir()
        
        metadata = {
            "name": "git-workflow",
            "description": "Git workflow automation"
        }
        with open(skill_dir / "skill.json", "w") as f:
            json.dump(metadata, f)
        
        loader = SkillLoader(str(tmp_path))
        results = loader.search_skills("automation")
        
        assert len(results) == 1
        assert results[0].name == "git-workflow"
    
    def test_search_skills_by_tags(self, tmp_path):
        """Test searching skills by tags."""
        skill_dir = tmp_path / "search-test"
        skill_dir.mkdir()
        
        metadata = {
            "name": "search-test",
            "description": "Test skill",
            "tags": ["python", "automation", "ci"]
        }
        with open(skill_dir / "skill.json", "w") as f:
            json.dump(metadata, f)
        
        loader = SkillLoader(str(tmp_path))
        results = loader.search_skills("ci")
        
        assert len(results) == 1
        assert results[0].name == "search-test"
    
    def test_execute_skill(self, tmp_path):
        """Test executing a skill."""
        skill_dir = tmp_path / "exec-test"
        skill_dir.mkdir()
        
        metadata = {"name": "exec-test", "description": "Test execution"}
        with open(skill_dir / "skill.json", "w") as f:
            json.dump(metadata, f)
        
        with open(skill_dir / "skill.py", "w") as f:
            f.write("""
def main(context=None):
    return {"result": "executed", "context": context}
""")
        
        loader = SkillLoader(str(tmp_path))
        result = loader.execute_skill("exec-test", context={"test": True})
        
        assert result["result"] == "executed"
        assert result["context"]["test"] is True
    
    def test_execute_nonexistent_skill(self, tmp_path):
        """Test executing a nonexistent skill raises error."""
        loader = SkillLoader(str(tmp_path))
        
        with pytest.raises(ValueError, match="not found"):
            loader.execute_skill("nonexistent")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])