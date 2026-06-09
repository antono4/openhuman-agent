#!/usr/bin/env python3
"""
OpenHuman CLI - Command line interface for the AI agent.

Usage:
    python -m src.cli <command> [options]
    
Commands:
    agent list           List available agents
    agent show <name>    Show agent definition
    skill list           List available skills
    skill run <name>     Execute a skill
    config show          Show current configuration
    config set <key> <value>  Set configuration value
"""

import sys
import json
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import Agent, create_agent, SkillLoader, AgentConfig


def cmd_agent_list(args):
    """List all available agents."""
    agent = create_agent()
    agents = agent.list_agents()
    
    if not agents:
        print("No agents found in .agents/agents/")
        return 0
    
    print("Available agents:")
    for name in agents:
        agent_def = agent.get_agent(name)
        print(f"  - {name}: {agent_def['description']}")
    
    return 0


def cmd_agent_show(args):
    """Show agent definition."""
    agent = create_agent()
    agent_def = agent.get_agent(args.name)
    
    if not agent_def:
        print(f"Agent '{args.name}' not found", file=sys.stderr)
        return 1
    
    print(f"Name: {agent_def['name']}")
    print(f"Description: {agent_def['description']}")
    print(f"Model: {agent_def['model']}")
    print(f"File: {agent_def['filepath']}")
    print()
    print(agent_def['content'])
    
    return 0


def cmd_skill_list(args):
    """List all available skills."""
    loader = SkillLoader()
    skills = loader.list_skills()
    
    if not skills:
        print("No skills found in .agents/skills/")
        return 0
    
    print("Available skills:")
    for name in skills:
        skill = loader.get_skill(name)
        print(f"  - {name}")
        print(f"    Category: {skill.category}")
        print(f"    Description: {skill.description}")
        print(f"    Tags: {', '.join(skill.tags)}")
        print()
    
    return 0


def cmd_skill_run(args):
    """Execute a skill."""
    loader = SkillLoader()
    skill = loader.get_skill(args.name)
    
    if not skill:
        print(f"Skill '{args.name}' not found", file=sys.stderr)
        return 1
    
    # Parse context from JSON file or arguments
    context = {}
    if args.context:
        context = json.loads(args.context)
    
    try:
        result = skill.execute(context=context)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        print(f"Error executing skill: {e}", file=sys.stderr)
        return 1


def cmd_config_show(args):
    """Show current configuration."""
    config = AgentConfig()
    
    print("Current configuration:")
    print(f"  action_dir: {config.action_dir}")
    print(f"  workspace_dir: {config.workspace_dir}")
    print(f"  autonomy_level: {config.autonomy_level}")
    print(f"  approval_gate_enabled: {config.approval_gate_enabled}")
    print(f"  allow_tool_install: {config.allow_tool_install}")
    
    return 0


def cmd_classify(args):
    """Classify a command."""
    agent = create_agent()
    
    result = agent.classify_command(args.command)
    
    print(f"Command: {args.command}")
    print(f"Classification: {result.classification}")
    print(f"Risk Level: {result.risk_level}")
    print(f"Requires Approval: {result.requires_approval}")
    
    decision = agent.gate_decision(result)
    print(f"Decision: {decision}")
    
    return 0


def cmd_execute(args):
    """Execute a command with security checks."""
    agent = create_agent()
    
    result = agent.execute_command(args.command)
    
    if result.get("blocked"):
        print(f"BLOCKED: {result['reason']}")
        return 1
    
    if result.get("requires_approval"):
        print(f"REQUIRES APPROVAL: {result['reason']}")
        return 1
    
    if result["success"]:
        if result.get("stdout"):
            print(result["stdout"])
        return 0
    else:
        if result.get("error"):
            print(f"ERROR: {result['error']}", file=sys.stderr)
        if result.get("stderr"):
            print(result["stderr"], file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="OpenHuman CLI - AI Agent Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.cli agent list
  python -m src.cli agent show pr-manager
  python -m src.cli skill list
  python -m src.cli skill run github-pr-manager --context '{"action": "list"}'
  python -m src.cli classify "git status"
  python -m src.cli execute "git status"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Agent subcommand
    agent_parser = subparsers.add_parser("agent", help="Agent operations")
    agent_subparsers = agent_parser.add_subparsers(dest="agent_command")
    
    agent_list_parser = agent_subparsers.add_parser("list", help="List agents")
    agent_list_parser.set_defaults(func=cmd_agent_list)
    
    agent_show_parser = agent_subparsers.add_parser("show", help="Show agent definition")
    agent_show_parser.add_argument("name", help="Agent name")
    agent_show_parser.set_defaults(func=cmd_agent_show)
    
    # Skill subcommand
    skill_parser = subparsers.add_parser("skill", help="Skill operations")
    skill_subparsers = skill_parser.add_subparsers(dest="skill_command")
    
    skill_list_parser = skill_subparsers.add_parser("list", help="List skills")
    skill_list_parser.set_defaults(func=cmd_skill_list)
    
    skill_run_parser = skill_subparsers.add_parser("run", help="Run a skill")
    skill_run_parser.add_argument("name", help="Skill name")
    skill_run_parser.add_argument("--context", help="JSON context for skill")
    skill_run_parser.set_defaults(func=cmd_skill_run)
    
    # Config subcommand
    config_parser = subparsers.add_parser("config", help="Configuration operations")
    config_subparsers = config_parser.add_subparsers(dest="config_command")
    
    config_show_parser = config_subparsers.add_parser("show", help="Show configuration")
    config_show_parser.set_defaults(func=cmd_config_show)
    
    # Classify subcommand
    classify_parser = subparsers.add_parser("classify", help="Classify a command")
    classify_parser.add_argument("command", help="Command to classify")
    classify_parser.set_defaults(func=cmd_classify)
    
    # Execute subcommand
    execute_parser = subparsers.add_parser("execute", help="Execute a command")
    execute_parser.add_argument("command", help="Command to execute")
    execute_parser.set_defaults(func=cmd_execute)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if hasattr(args, "func"):
        return args.func(args)
    
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())