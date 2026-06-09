# OpenHuman AI Agent

A desktop AI agent inspired by [openhuman](https://github.com/tinyhumansai/openhuman), providing intelligent automation for development workflows, code review, and task management.

## Features

- **Agent-based Architecture**: Define agents as markdown files with YAML frontmatter
- **Skill System**: Reusable skill modules that agents can invoke dynamically
- **Security**: Command classification and approval gates for safe execution
- **Git Integration**: Built-in tools for Git operations and PR management
- **CLI Interface**: Command-line tool for agent and skill management

## Project Structure

```
.
├── .agents/
│   ├── agents/           # Agent definitions (markdown files)
│   │   ├── ship-and-babysit.md
│   │   ├── pr-manager.md
│   │   └── pr-manager-lite.md
│   └── skills/           # Reusable skill modules
│       ├── github-pr-manager/
│       └── git-workflow/
├── src/
│   ├── __init__.py       # Package initialization
│   ├── agent.py          # Core Agent class
│   ├── cli.py            # CLI interface
│   ├── skill_loader.py   # Skill loading system
│   └── tools.py          # Tool implementations
├── tests/                # Test suite
├── docs/                 # Documentation
├── AGENTS.md             # Agent guidelines
└── package.json          # Project metadata
```

## Quick Start

### List Available Agents

```bash
python -m src.cli agent list
```

### Show Agent Definition

```bash
python -m src.cli agent show pr-manager
```

### List Available Skills

```bash
python -m src.cli skill list
```

### Execute a Skill

```bash
python -m src.cli skill run github-pr-manager --context '{"action": "list"}'
```

### Classify a Command

```bash
python -m src.cli classify "git commit -m 'fix bug'"
```

## Available Agents

### ship-and-babysit

Commits changes, pushes branch, opens PR, and monitors CI until green.

### pr-manager

Completes PRs by applying reviewer feedback, running checks, and pushing fixes.

### pr-manager-lite

Same as pr-manager but assumes the PR branch is already checked out locally.

## Available Skills

### github-pr-manager

Manage GitHub pull requests:
- `action: "list"` - List open PRs
- `action: "view"` - View PR details
- `action: "create"` - Create a new PR
- `action: "checks"` - Get PR check status
- `action: "merge"` - Merge a PR

### git-workflow

Git operations:
- `action: "status"` - Get git status
- `action: "diff"` - Get git diff
- `action: "commit"` - Create a commit
- `action: "push"` - Push to remote
- `action: "pull"` - Pull from remote
- `action: "branch"` - List branches
- `action: "checkout"` - Checkout a branch

## Programmatic Usage

```python
from src import create_agent, SkillLoader

# Create an agent
agent = create_agent()

# List available agents
print(agent.list_agents())

# Get an agent definition
pr_manager = agent.get_agent("pr-manager")
print(pr_manager["description"])

# Classify a command
result = agent.classify_command("git status")
print(f"Classification: {result.classification}")

# Execute with security checks
result = agent.execute_command("git status")
print(f"Success: {result['success']}")

# Load and execute skills
loader = SkillLoader()
skill = loader.get_skill("github-pr-manager")
result = skill.execute(context={"action": "list"})
```

## Security

### Command Classification

Commands are classified into categories:
- **Read**: git status, cat, ls, grep
- **Write**: touch, mkdir, git commit, git add
- **Network**: curl, wget, git fetch, git pull
- **Install**: npm install, pip install
- **Destructive**: rm -rf, git reset --hard

### Autonomy Levels

- **readonly**: Only allows Read operations
- **supervised**: Allows Read/Write/Network with approval for Install/Destructive
- **full**: Allows all operations with approval for Destructive only

### Approval Gate

Commands requiring approval are parked and await user confirmation before execution.

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_agent.py -v

# Run tests with coverage
python -m pytest tests/ --cov=src
```

## Windows Executable (.exe)

Pre-built executable tersedia di folder `release/openhuman-agent-win64/`

### Cara Menjalankan di Windows

1. **Buka Command Prompt (CMD)**
   - Tekan `Windows + R`
   - Ketik `cmd`, tekan Enter

2. **Navigasi ke folder executable**
   ```cmd
   cd path\to\openhuman-agent-win64
   ```

3. **Jalankan perintah**
   ```cmd
   # List agents
   openhuman-agent.exe agent list

   # List skills
   openhuman-agent.exe skill list

   # Classify command (cek keamanan)
   openhuman-agent.exe classify "rm -rf /temp"

   # Git status
   openhuman-agent.exe execute "git status"
   ```

4. **Atau gunakan run.bat** untuk menu interaktif
   ```cmd
   run.bat
   ```

### Build Ulang di Windows

```cmd
# Install Python dari python.org (3.10+)
# Buka CMD, navigasi ke project folder
pip install pyinstaller
build.bat
```

## License

MIT