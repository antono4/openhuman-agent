# OpenHuman AI Agent

**AI assistant for communities — Desktop AI agent with human-like capabilities.**

---

## Repository Layout

| Path | Role |
|------|------|
| `.agents/agents/` | Agent definition files (markdown-based AI agents) |
| `.agents/skills/` | Reusable skill modules for agents |
| `src/` | Core agent implementation |
| `docs/` | Documentation |

---

## Commands

```bash
# Development
npm run dev

# Testing
npm test

# Build
npm run build
```

---

## Agent Access & Security

**Two path roots:**

- **`action_dir`** — agent's read/write root. Acting tools resolve relative paths here. Default: `~/OpenHuman/projects`
- **`workspace_dir`** — internal state. Agent tools **cannot** write here.

**Command permission model**: Classify commands into `Read`/`Write`/`Network`/`Install`/`Destructive`. Unrecognized = `Write`.

**Approval gate**: ON by default. Parks interactive chat turns only.

---

## Testing

- Unit tests co-located as `*.test.ts`
- E2E tests in `tests/e2e/`
- Mock services for external dependencies

---

## Architecture

### Agent System

Agents are defined as markdown files in `.agents/agents/`. Each agent has:

1. **Frontmatter** — `name`, `description`, `model`
2. **System prompt** — Role and behavior definition
3. **Workflow phases** — Step-by-step instructions
4. **Guardrails** — Safety constraints

### Skills System

Skills are reusable modules in `.agents/skills/` that agents can invoke:

- File-based skills as Python modules
- JSON metadata in `skill.json`
- Dynamic invocation via `invoke_skill` tool

---

## Code Standards

- TypeScript for application code
- Python for skill modules
- Comprehensive logging without secrets
- Files under 500 lines preferred
- Tests for new functionality