# OpenHuman AI Agent - Documentation

## Overview

OpenHuman is a desktop AI agent inspired by the openhuman project. It provides intelligent automation for development workflows, code review, and task management.

## Quick Start

```bash
# List available agents
python src/agent.py

# Run a specific agent
python src/agent.py pr-manager

# Use the agent programmatically
from src import create_agent

agent = create_agent()
print(agent.list_agents())
```

## Architecture

### Agents

Agents are defined as markdown files in `.agents/agents/`. Each agent has:

1. **Frontmatter** - Metadata (name, description, model)
2. **System prompt** - Role and behavior definition
3. **Workflow phases** - Step-by-step instructions
4. **Guardrails** - Safety constraints

### Skills

Skills are reusable modules in `.agents/skills/` that agents can invoke. Each skill has:

- `skill.json` - Metadata and configuration schema
- `skill.py` - Python implementation with `main()` entry point

## Available Agents

### ship-and-babysit

Commits changes, pushes branch, opens PR, and monitors CI until green.

### pr-manager

Completes PRs by applying reviewer feedback, running checks, and pushing fixes.

### pr-manager-lite

Same as pr-manager but assumes the PR branch is already checked out locally.

## Available Skills

### github-pr-manager

Manage GitHub pull requests - create, view, merge, close.

### git-workflow

Git operations - commit, branch, push, pull, history.

## Configuration

### Agent Configuration

```python
from src import AgentConfig, create_agent

config = AgentConfig(
    action_dir="~/my-projects",      # Agent's read/write root
    workspace_dir="~/.my-workspace", # Internal state (read-only for tools)
    autonomy_level="supervised",     # readonly, supervised, or full
    approval_gate_enabled=True       # Park interactive turns for approval
)

agent = create_agent(config)
```

### Command Classification

Commands are classified into categories:
- **Read**: git status, cat, ls
- **Write**: touch, mkdir, git commit
- **Network**: curl, wget, git fetch
- **Install**: npm install, pip install
- **Destructive**: rm, git reset --hard

### Autonomy Levels

- **readonly**: Only allows Read operations
- **supervised**: Allows Read/Write/Network with approval for Install/Destructive
- **full**: Allows all operations with approval for Destructive only

## Development

### Adding a New Agent

1. Create a markdown file in `.agents/agents/`
2. Add frontmatter with name, description, model
3. Write the agent behavior in markdown

```markdown
---
name: my-agent
description: What this agent does
model: inherit
---

# My Agent

Your agent behavior definition here...
```

### Adding a New Skill

1. Create a directory in `.agents/skills/`
2. Add `skill.json` with metadata
3. Add `skill.py` with `main()` function

```json
{
  "name": "my-skill",
  "description": "What this skill does",
  "category": "development",
  "version": "1.0.0",
  "entry_point": "main"
}
```

```python
def main(context=None):
    return {"status": "success", "message": "Hello from my skill!"}
```

## Security

### Path Isolation

- **action_dir**: Agent's read/write root. Default: `~/OpenHuman/projects`
- **workspace_dir**: Internal state directory. Default: `~/.openhuman/workspace`

### Command Approval

Commands requiring approval are parked and await user confirmation before execution.

### Secret Protection

Never commit secrets, credentials, or API keys to the repository.