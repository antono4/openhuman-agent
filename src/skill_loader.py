"""
OpenHuman AI Agent - Skill Loader

Loads and manages reusable skill modules that agents can invoke.
Skills are defined as Python modules with metadata in skill.json.
"""

import os
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field


@dataclass
class Skill:
    """Represents a skill module with metadata and callable functions."""
    
    name: str
    description: str
    category: str = "general"
    version: str = "1.0.0"
    author: str = ""
    tags: List[str] = field(default_factory=list)
    
    # The actual skill module/function
    module: Optional[Any] = None
    callable: Optional[Callable] = None
    
    # Metadata file path
    filepath: str = ""
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute the skill's main function."""
        if self.callable:
            return self.callable(*args, **kwargs)
        raise NotImplementedError(f"Skill '{self.name}' has no callable function")


@dataclass
class SkillMetadata:
    """Metadata for a skill defined in skill.json."""
    
    name: str
    description: str
    category: str = "general"
    version: str = "1.0.0"
    author: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Entry point for the skill
    entry_point: str = "main"
    
    # Dependencies
    requires: List[str] = field(default_factory=list)
    
    # Configuration options
    config_schema: Optional[Dict] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SkillMetadata':
        """Create SkillMetadata from a dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=data.get("category", "general"),
            version=data.get("version", "1.0.0"),
            author=data.get("author", ""),
            tags=data.get("tags", []),
            entry_point=data.get("entry_point", "main"),
            requires=data.get("requires", []),
            config_schema=data.get("config_schema")
        )


class SkillLoader:
    """
    Loads and manages skill modules from .agents/skills/ directory.
    
    Skills are discovered by looking for skill.json files and
    corresponding Python modules.
    """
    
    def __init__(self, skills_dir: str = ".agents/skills"):
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Skill] = {}
        self._load_all()
    
    def _load_all(self):
        """Discover and load all skills in the skills directory."""
        if not self.skills_dir.exists():
            return
        
        for skill_path in self.skills_dir.iterdir():
            if skill_path.is_dir():
                self._load_skill(skill_path)
    
    def _load_skill(self, skill_path: Path):
        """Load a single skill from a directory."""
        # Look for skill.json
        metadata_file = skill_path / "skill.json"
        py_file = skill_path / "skill.py"
        
        if not metadata_file.exists():
            return
        
        try:
            # Load metadata
            with open(metadata_file, 'r') as f:
                metadata_data = json.load(f)
            
            metadata = SkillMetadata.from_dict(metadata_data)
            
            # Load Python module if exists
            skill = Skill(
                name=metadata.name,
                description=metadata.description,
                category=metadata.category,
                version=metadata.version,
                author=metadata.author,
                tags=metadata.tags,
                filepath=str(skill_path)
            )
            
            if py_file.exists():
                # Load the Python module
                spec = importlib.util.spec_from_file_location(
                    f"skill_{metadata.name}",
                    py_file
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Get the entry point function
                    entry = getattr(module, metadata.entry_point, None)
                    if entry and callable(entry):
                        skill.module = module
                        skill.callable = entry
            
            self.skills[metadata.name] = skill
            
        except Exception as e:
            print(f"Error loading skill from {skill_path}: {e}")
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name."""
        return self.skills.get(name)
    
    def list_skills(self, category: Optional[str] = None) -> List[str]:
        """List all available skill names, optionally filtered by category."""
        if category:
            return [
                name for name, skill in self.skills.items()
                if skill.category == category
            ]
        return list(self.skills.keys())
    
    def list_categories(self) -> List[str]:
        """List all skill categories."""
        return list(set(skill.category for skill in self.skills.values()))
    
    def search_skills(self, query: str) -> List[Skill]:
        """Search skills by name, description, or tags."""
        query_lower = query.lower()
        results = []
        
        for skill in self.skills.values():
            if query_lower in skill.name.lower():
                results.append(skill)
            elif query_lower in skill.description.lower():
                results.append(skill)
            elif any(query_lower in tag.lower() for tag in skill.tags):
                results.append(skill)
        
        return results
    
    def execute_skill(self, name: str, *args, **kwargs) -> Any:
        """Execute a skill by name."""
        skill = self.get_skill(name)
        if not skill:
            raise ValueError(f"Skill '{name}' not found")
        return skill.execute(*args, **kwargs)


# Example skill template
EXAMPLE_SKILL_METADATA = {
    "name": "example-skill",
    "description": "An example skill that demonstrates the skill system",
    "category": "development",
    "version": "1.0.0",
    "author": "OpenHuman",
    "tags": ["example", "template"],
    "entry_point": "main",
    "requires": []
}

EXAMPLE_SKILL_PYTHON = '''
"""Example skill - demonstrates skill system."""

def main(context: dict = None) -> dict:
    """
    Main entry point for the skill.
    
    Args:
        context: Optional context dictionary with skill parameters
    
    Returns:
        dict: Result of skill execution
    """
    return {
        "status": "success",
        "message": "Example skill executed successfully",
        "context": context or {}
    }


# Allow skill to be called directly
if __name__ == "__main__":
    result = main()
    print(result)
'''