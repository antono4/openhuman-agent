"""
OpenHuman AI Agent - Core Agent Implementation

A desktop AI agent with human-like capabilities for task automation,
code review, and development workflow management.
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    """Configuration for agent behavior and permissions."""
    
    # Path roots
    action_dir: str = os.path.expanduser("~/OpenHuman/projects")
    workspace_dir: str = os.path.expanduser("~/.openhuman/workspace")
    
    # Autonomy levels: readonly, supervised, full
    autonomy_level: str = "supervised"
    
    # Approval gate (parks interactive turns)
    approval_gate_enabled: bool = True
    
    # Trusted roots for file access
    trusted_roots: List[str] = field(default_factory=list)
    
    # Allow tool installation
    allow_tool_install: bool = False


@dataclass
class CommandClassification:
    """Classification of a command into permission categories."""
    
    command: str
    classification: str  # Read, Write, Network, Install, Destructive
    risk_level: str      # LOW, MEDIUM, HIGH
    requires_approval: bool = False


class Agent:
    """
    Core AI Agent with tools and workflow management.
    
    Agents are defined as markdown files with frontmatter:
    ---
    name: agent-name
    description: What this agent does
    model: inherit
    ---
    
    # Agent Name
    
    Agent behavior definition...
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self._load_agents()
    
    def _load_agents(self):
        """Load agent definitions from .agents/agents/ directory."""
        agents_dir = Path(".agents/agents")
        self.agents: Dict[str, Dict] = {}
        
        if agents_dir.exists():
            for agent_file in agents_dir.glob("*.md"):
                agent_def = self._parse_agent_file(agent_file)
                if agent_def:
                    self.agents[agent_def["name"]] = agent_def
    
    def _parse_agent_file(self, filepath: Path) -> Optional[Dict]:
        """Parse a markdown agent definition file."""
        try:
            content = filepath.read_text()
            
            # Parse frontmatter
            frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not frontmatter_match:
                return None
            
            frontmatter = {}
            for line in frontmatter_match.group(1).split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()
            
            # Extract markdown content (everything after frontmatter)
            markdown_content = content[frontmatter_match.end():].strip()
            
            return {
                "name": frontmatter.get("name", filepath.stem),
                "description": frontmatter.get("description", ""),
                "model": frontmatter.get("model", "inherit"),
                "content": markdown_content,
                "filepath": str(filepath)
            }
        except Exception as e:
            print(f"Error parsing agent file {filepath}: {e}")
            return None
    
    def get_agent(self, name: str) -> Optional[Dict]:
        """Get an agent definition by name."""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all available agent names."""
        return list(self.agents.keys())
    
    def classify_command(self, command: str) -> CommandClassification:
        """
        Classify a command into permission categories.
        
        Categories:
        - Read: Read-only operations (git status, cat, ls)
        - Write: File creation/modification (touch, echo, mkdir)
        - Network: Network operations (curl, wget, git fetch)
        - Install: Package installation (npm install, pip install)
        - Destructive: Potentially destructive (rm, git reset --hard)
        """
        command_lower = command.lower().strip()
        
        # Read operations
        read_patterns = [
            r'^(ls|ll|la|cat|head|tail|grep|find|git status|git log|git show|git diff|git branch|pwd|which|whoami)',
        ]
        
        # Write operations
        write_patterns = [
            r'^(touch|mkdir|echo|printf|tee|cp|mv|chmod|chown|git add|git commit|git push)',
        ]
        
        # Network operations
        network_patterns = [
            r'^(curl|wget|ssh|rsync|scp|git fetch|git pull)',
        ]
        
        # Install operations
        install_patterns = [
            r'^(npm install|yarn add|pip install|pip3 install|apt-get install|yum install)',
        ]
        
        # Destructive operations
        destructive_patterns = [
            r'^(rm|rm -rf|del|git reset --hard|git clean|dd|mkfs)',
        ]
        
        for pattern in destructive_patterns:
            if re.match(pattern, command_lower):
                return CommandClassification(
                    command=command,
                    classification="Destructive",
                    risk_level="HIGH",
                    requires_approval=True
                )
        
        for pattern in install_patterns:
            if re.match(pattern, command_lower):
                return CommandClassification(
                    command=command,
                    classification="Install",
                    risk_level="MEDIUM",
                    requires_approval=True
                )
        
        for pattern in network_patterns:
            if re.match(pattern, command_lower):
                return CommandClassification(
                    command=command,
                    classification="Network",
                    risk_level="LOW",
                    requires_approval=False
                )
        
        for pattern in write_patterns:
            if re.match(pattern, command_lower):
                return CommandClassification(
                    command=command,
                    classification="Write",
                    risk_level="LOW",
                    requires_approval=False
                )
        
        for pattern in read_patterns:
            if re.match(pattern, command_lower):
                return CommandClassification(
                    command=command,
                    classification="Read",
                    risk_level="LOW",
                    requires_approval=False
                )
        
        # Default to Write classification
        return CommandClassification(
            command=command,
            classification="Write",
            risk_level="MEDIUM",
            requires_approval=True
        )
    
    def gate_decision(self, classification: CommandClassification) -> str:
        """
        Gate a command decision based on autonomy level and classification.
        
        Returns: Allow, Prompt, Block
        """
        if self.config.autonomy_level == "readonly":
            if classification.classification in ["Write", "Install", "Destructive"]:
                return "Block"
            return "Prompt"
        
        elif self.config.autonomy_level == "supervised":
            if classification.requires_approval:
                return "Prompt"
            return "Allow"
        
        elif self.config.autonomy_level == "full":
            if classification.classification == "Destructive":
                return "Prompt"
            return "Allow"
        
        return "Block"
    
    def execute_command(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a shell command with safety checks.
        
        Returns dict with success status, output, and error info.
        """
        # Classify the command
        classification = self.classify_command(command)
        
        # Gate the decision
        decision = self.gate_decision(classification)
        
        if decision == "Block":
            return {
                "success": False,
                "blocked": True,
                "reason": f"Command '{command}' blocked by security policy",
                "classification": classification.classification,
                "decision": decision
            }
        
        if decision == "Prompt":
            return {
                "success": False,
                "requires_approval": True,
                "reason": f"Command '{command}' requires approval",
                "classification": classification.classification,
                "decision": decision
            }
        
        # Execute the command
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or os.getcwd(),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "classification": classification.classification,
                "decision": decision
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 300 seconds",
                "classification": classification.classification,
                "decision": decision
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "classification": classification.classification,
                "decision": decision
            }


def create_agent(config: Optional[AgentConfig] = None) -> Agent:
    """Factory function to create an agent instance."""
    return Agent(config)


# CLI interface
if __name__ == "__main__":
    import sys
    
    agent = create_agent()
    
    print("OpenHuman AI Agent")
    print("=" * 40)
    print(f"Available agents: {', '.join(agent.list_agents())}")
    print()
    
    if len(sys.argv) > 1:
        agent_name = sys.argv[1]
        agent_def = agent.get_agent(agent_name)
        if agent_def:
            print(f"Agent: {agent_def['name']}")
            print(f"Description: {agent_def['description']}")
            print()
            print(agent_def['content'])
        else:
            print(f"Agent '{agent_name}' not found")
    else:
        print("Usage: python src/agent.py <agent-name>")
        print("Available agents:")
        for name in agent.list_agents():
            agent_def = agent.get_agent(name)
            print(f"  - {name}: {agent_def['description']}")