"""
OpenHuman AI Agent

A desktop AI agent with human-like capabilities.
"""

from .agent import Agent, AgentConfig, create_agent
from .tools import Tools, ToolResult
from .skill_loader import SkillLoader, Skill

__version__ = "0.1.0"

__all__ = [
    "Agent",
    "AgentConfig", 
    "create_agent",
    "Tools",
    "ToolResult",
    "SkillLoader",
    "Skill"
]