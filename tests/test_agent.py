"""Tests for the OpenHuman AI Agent."""

import pytest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import Agent, AgentConfig, create_agent


class TestAgentConfig:
    """Tests for AgentConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = AgentConfig()
        assert config.autonomy_level == "supervised"
        assert config.approval_gate_enabled is True
        assert config.allow_tool_install is False
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = AgentConfig(
            action_dir="/custom/path",
            workspace_dir="/custom/workspace",
            autonomy_level="full"
        )
        assert config.action_dir == "/custom/path"
        assert config.workspace_dir == "/custom/workspace"
        assert config.autonomy_level == "full"


class TestAgent:
    """Tests for Agent class."""
    
    def test_create_agent(self):
        """Test agent creation."""
        agent = create_agent()
        assert isinstance(agent, Agent)
    
    def test_list_agents(self):
        """Test listing agents."""
        agent = create_agent()
        agents = agent.list_agents()
        assert isinstance(agents, list)
    
    def test_classify_read_command(self):
        """Test command classification for read operations."""
        agent = create_agent()
        result = agent.classify_command("git status")
        assert result.classification == "Read"
        assert result.risk_level == "LOW"
        assert result.requires_approval is False
    
    def test_classify_write_command(self):
        """Test command classification for write operations."""
        agent = create_agent()
        result = agent.classify_command("git commit -m 'test'")
        assert result.classification == "Write"
        assert result.risk_level == "LOW"
    
    def test_classify_network_command(self):
        """Test command classification for network operations."""
        agent = create_agent()
        result = agent.classify_command("curl https://api.example.com")
        assert result.classification == "Network"
    
    def test_classify_install_command(self):
        """Test command classification for install operations."""
        agent = create_agent()
        result = agent.classify_command("npm install")
        assert result.classification == "Install"
        assert result.requires_approval is True
    
    def test_classify_destructive_command(self):
        """Test command classification for destructive operations."""
        agent = create_agent()
        result = agent.classify_command("rm -rf /tmp/test")
        assert result.classification == "Destructive"
        assert result.risk_level == "HIGH"
        assert result.requires_approval is True
    
    def test_classify_unknown_command(self):
        """Test command classification for unknown operations."""
        agent = create_agent()
        result = agent.classify_command("some_unknown_command")
        assert result.classification == "Write"  # Default
        assert result.risk_level == "MEDIUM"
    
    def test_gate_decision_readonly(self):
        """Test gate decision for readonly autonomy."""
        config = AgentConfig(autonomy_level="readonly")
        agent = Agent(config)
        
        result = agent.classify_command("git status")
        decision = agent.gate_decision(result)
        assert decision == "Prompt"  # Read is allowed with prompt
        
        result = agent.classify_command("touch file.txt")
        decision = agent.gate_decision(result)
        assert decision == "Block"  # Write is blocked
    
    def test_gate_decision_supervised(self):
        """Test gate decision for supervised autonomy."""
        config = AgentConfig(autonomy_level="supervised")
        agent = Agent(config)
        
        result = agent.classify_command("git status")
        decision = agent.gate_decision(result)
        assert decision == "Allow"
        
        result = agent.classify_command("npm install")
        decision = agent.gate_decision(result)
        assert decision == "Prompt"  # Install requires approval
    
    def test_gate_decision_full(self):
        """Test gate decision for full autonomy."""
        config = AgentConfig(autonomy_level="full")
        agent = Agent(config)
        
        result = agent.classify_command("git status")
        decision = agent.gate_decision(result)
        assert decision == "Allow"
        
        result = agent.classify_command("touch file.txt")
        decision = agent.gate_decision(result)
        assert decision == "Allow"
        
        result = agent.classify_command("rm -rf test")
        decision = agent.gate_decision(result)
        assert decision == "Prompt"  # Destructive still requires approval


class TestAgentExecution:
    """Tests for agent command execution."""
    
    def test_blocked_command(self):
        """Test that blocked commands are rejected."""
        config = AgentConfig(autonomy_level="readonly")
        agent = Agent(config)
        
        result = agent.execute_command("touch test.txt")
        assert result["success"] is False
        assert result["blocked"] is True
    
    def test_readonly_command(self):
        """Test that readonly commands pass through."""
        config = AgentConfig(autonomy_level="full")
        agent = Agent(config)
        
        result = agent.execute_command("pwd")
        # pwd should be allowed (classified as Read)
        assert result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])