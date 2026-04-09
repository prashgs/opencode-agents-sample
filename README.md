# WebGen Agent 🤖

An autonomous multi-agent system that builds web applications from natural language prompts.
Powered by **OpenCode** (agent execution + file writing) and **Ollama** (local LLMs).

---

## Architecture

```
User Prompt
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Python Orchestrator  (main.py / loop.py)           │
│                                                     │
│  Starts ──▶  opencode serve  (port 4096)            │
│              │                                      │
│              │  Session                             │
│              │                                      │
│    ┌─────────┴──────────────────────┐               │
│    │        Agentic Loop            │               │
│    │                                │               │
│    │  @web-planner                  │               │
│    │   └─ skill: web-planner        │               │
│    │   └─ returns JSON build plan   │               │
│    │                                │               │
│    │  @web-app-builder  ◀──────┐    │               │
│    │   └─ skill: web-app-builder│    │               │
│    │   └─ writes files to disk  │    │               │
│    │                            │    │               │
│    │  @web-reviewer         feedback │               │
│    │   └─ skill: web-reviewer   │    │               │
│    │   └─ reads files, returns JSON  │               │
│    │   └─ approved? ──No────────┘    │               │
│    │              │ Yes              │               │
│    │              ▼                  │               │
│    │  @web-writer                    │               │
│    │   └─ skill: web-writer          │               │
│    │   └─ writes README.md           │               │
│    └────────────────────────────────┘               │
└─────────────────────────────────────────────────────┘
    │
    ▼
output/<app-name>/
  index.html, style.css, app.js, README.md
  (+ app.py, models.py, etc. if backend)
```

### Key Design Principle

**OpenCode does the writing. Python does the directing.**

- All file I/O (HTML, CSS, JS, Python, README) is done by OpenCode subagents using their native `write` and `edit` tools
- Python manages session lifecycle, the review loop, and feedback routing
- Agent behaviour is controlled entirely by `.opencode/agents/*.md` and `.opencode/skills/*/SKILL.md` files — no Python changes needed to tune agents

---

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Orchestration |
| Node.js | 18+ | Required to install OpenCode |
| OpenCode | Latest | Agent execution engine |
| Ollama | Latest | Local LLM inference |

**Hardware:** RTX 4060 8GB recommended. Models load one at a time so VRAM is not a bottleneck.

---

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/yourname/webgen-agent.git
cd webgen-agent
```

### 2. Run the setup script

```bash
bash setup.sh
```

This will:
- Install OpenCode CLI (via npm or install script)
- Check Ollama is installed
- Pull the three required Ollama models (~12GB total, one-time)
- Install Python dependencies
- Print instructions to set `LOCAL_ENDPOINT`

### 3. Set LOCAL_ENDPOINT (required for Ollama + OpenCode)

Add this to your `~/.bashrc` or `~/.zshrc`:

```bash
export LOCAL_ENDPOINT=http://localhost:11434/v1
```

Then reload:

```bash
source ~/.bashrc   # or source ~/.zshrc
```

OpenCode reads `LOCAL_ENDPOINT` at startup to discover your local Ollama models.

### 4. Start Ollama

```bash
ollama serve
```

Keep this running in a terminal while you use WebGen Agent.

### 5. Verify everything is ready

```bash
python main.py --check
```

Expected output:
```
  ✅  opencode CLI         found
  ✅  ollama               found
  ✅  ollama server        running (3 models)
  ✅  qwen2.5-coder:7b     ok
  ✅  granite-code:8b      ok
  ✅  nemotron-mini:4b     ok
  ✅  opencode.json        found
  ✅  .opencode/agents/    4 agent(s)
  ✅  .opencode/skills/    4 skill(s)
  ✅  All checks passed!
```

---

## Usage

### Build from a prompt file

```bash
python main.py prompts/todo_app.prompt.md
python main.py prompts/notes_app.prompt.md
python main.py prompts/expense_tracker.prompt.md   # FastAPI backend included
python main.py prompts/landing_page.prompt.md
```

### Build from an inline description

```bash
python main.py "Build a pomodoro timer with session history and stats"
python main.py "Build a markdown note editor with live preview"
python main.py "Build a budget planner with monthly income and expense categories"
```

### Interactive mode

```bash
python main.py
# → prompts you to type
```

### Other commands

```bash
python main.py --check           # preflight checks
python main.py --list-prompts    # list available .prompt.md files
python main.py --serve-only      # start OpenCode server, stay running for manual use
```

---

## Output

Generated apps appear in `output/<app-name>/`:

```
output/
└── todo-app/
    ├── index.html
    ├── style.css
    ├── app.js
    └── README.md

output/
└── expense-tracker/
    ├── index.html
    ├── style.css
    ├── app.js
    ├── app.py
    ├── models.py
    ├── database.py
    ├── requirements.txt
    ├── run.sh
    └── README.md
```

**Frontend-only apps** — open `index.html` in a browser. Done.

**Apps with a backend:**
```bash
cd output/expense-tracker
pip install -r requirements.txt
bash run.sh          # starts FastAPI on port 8000
# open index.html in browser
```

---

## Project Structure

```
webgen-agent/
│
├── .opencode/                      ← OpenCode project config
│   ├── agents/                     ← Custom OpenCode subagent definitions
│   │   ├── web-planner.md          ← Planner subagent (read-only, returns JSON)
│   │   ├── web-app-builder.md      ← Builder subagent (writes files to disk)
│   │   ├── web-reviewer.md         ← Reviewer subagent (reads files, returns verdict)
│   │   └── web-writer.md           ← Writer subagent (writes README.md)
│   └── skills/                     ← OpenCode skill files (loaded on-demand)
│       ├── web-planner/SKILL.md    ← Planner instructions + JSON schema
│       ├── web-app-builder/SKILL.md ← HTML/CSS/JS coding standards
│       ├── web-reviewer/SKILL.md   ← Review checklist + approval rules
│       └── web-writer/SKILL.md     ← README format and style
│
├── agents/                         ← Python agent wrappers
│   ├── base_agent.py               ← Base class: sends prompts to OpenCode subagents
│   ├── orchestrator.py             ← Master coordinator: manages session + loop
│   ├── planner.py                  ← Calls @web-planner, parses JSON plan
│   ├── frontend_agent.py           ← Calls @web-app-builder for HTML/CSS/JS
│   ├── backend_agent.py            ← Calls @web-app-builder for Python backend
│   ├── reviewer.py                 ← Calls @web-reviewer, parses JSON verdict
│   └── writer.py                   ← Calls @web-writer for README.md
│
├── tools/                          ← Utility modules
│   ├── opencode_client.py          ← HTTP client for opencode serve REST API
│   ├── opencode_server.py          ← Starts/stops opencode serve subprocess
│   ├── opencode_runner.py          ← Wraps `opencode run` CLI for one-shot mode
│   ├── file_writer.py              ← Parse <file> blocks, write to disk (fallback)
│   └── skill_loader.py             ← Load .skill.md content for logging/reference
│
├── prompts/                        ← Ready-to-use app blueprints
│   ├── todo_app.prompt.md
│   ├── notes_app.prompt.md
│   ├── expense_tracker.prompt.md
│   └── landing_page.prompt.md
│
├── output/                         ← Generated apps land here (git-ignored)
│
├── opencode.json                   ← OpenCode project config (models, agents, permissions)
├── config.yaml                     ← Python orchestrator config (port, iterations)
├── loop.py                         ← Thin wrapper: loads config, calls Orchestrator
├── main.py                         ← CLI entry point
├── requirements.txt                ← Python deps (requests, pyyaml)
└── setup.sh                        ← One-time installation script
```

---

## Configuration

### opencode.json — Agent & model config

This is the primary config file. It controls which Ollama model each OpenCode agent uses:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "local/qwen2.5-coder:7b",
  "agent": {
    "web-planner": {
      "model": "local/qwen2.5-coder:7b",
      "temperature": 0.1,
      "steps": 4
    },
    "web-app-builder": {
      "model": "local/qwen2.5-coder:7b",
      "temperature": 0.35,
      "steps": 12
    },
    "web-reviewer": {
      "model": "local/nemotron-mini:4b",
      "temperature": 0.1,
      "steps": 4
    },
    "web-writer": {
      "model": "local/qwen2.5-coder:7b",
      "temperature": 0.2,
      "steps": 3
    }
  }
}
```

Model names use the format `local/<ollama-model-name>` because OpenCode reads them
from Ollama via the `LOCAL_ENDPOINT` environment variable.

### config.yaml — Orchestrator config

```yaml
opencode_server_port: 4096
opencode_server_host: "127.0.0.1"
max_loop_iterations: 4
```

Increase `max_loop_iterations` for more thorough review-revise cycles.

### Swapping models

You can use any model pulled in Ollama:

```bash
ollama pull codellama:7b
```

Then update `opencode.json`:
```json
"web-app-builder": {
  "model": "local/codellama:7b"
}
```

Good alternatives for your RTX 4060 8GB:

| Role | Alternatives |
|---|---|
| Planner / Builder | `codellama:7b`, `deepseek-coder:6.7b`, `mistral:7b` |
| Backend | `codellama:13b` (needs 8GB VRAM), `deepseek-coder:6.7b` |
| Reviewer | `llama3.2:3b`, `phi3:mini` (very fast, lightweight) |

---

## Customizing Agents

### Skill files (`.opencode/skills/*/SKILL.md`)

Skill files control what agents know and how they format output. Edit them to change agent behaviour without touching Python.

| File | Controls |
|---|---|
| `web-planner/SKILL.md` | JSON schema for build plans, planning rules |
| `web-app-builder/SKILL.md` | HTML/CSS/JS standards, file writing rules |
| `web-reviewer/SKILL.md` | Review checklist, scoring, approval threshold |
| `web-writer/SKILL.md` | README structure and style |

### Agent files (`.opencode/agents/*.md`)

Agent files set the model, temperature, step limit, and tool permissions per agent.
The frontmatter controls OpenCode behaviour; the body is the system prompt.

```markdown
---
description: What this agent does (shown to the primary agent for routing)
mode: subagent
model: local/qwen2.5-coder:7b
temperature: 0.35
steps: 12
permission:
  write: allow
  edit: allow
  bash: allow
---

Your system prompt here...
```

### Adding a new agent

1. Create `.opencode/agents/my-agent.md` with frontmatter and system prompt
2. Create `.opencode/skills/my-agent/SKILL.md` with instructions
3. Add the agent to `opencode.json` under `"agent": { "my-agent": { ... } }`
4. Create a Python wrapper in `agents/my_agent.py` inheriting `BaseAgent`
5. Call it from `agents/orchestrator.py`

---

## How OpenCode + Ollama Works Together

OpenCode uses the `LOCAL_ENDPOINT` environment variable to connect to Ollama's
OpenAI-compatible API (`http://localhost:11434/v1`). In `opencode.json`, local
models are referenced as `local/<model-name>`.

```
LOCAL_ENDPOINT=http://localhost:11434/v1
                        │
                        ▼
opencode.json:  "model": "local/qwen2.5-coder:7b"
                              │
                              ▼
                    Ollama serves the model
```

No API keys needed. Everything runs locally.

---

## Using OpenCode Directly (without Python)

Once the server is running, you can also drive it manually:

```bash
# Start the server in one terminal
python main.py --serve-only

# In another terminal — run any agent directly
opencode run --attach http://localhost:4096 \
  --agent web-planner \
  "Build a recipe book app with search and categories"

opencode run --attach http://localhost:4096 \
  --agent web-app-builder \
  "Build index.html for a dark-themed todo app in output/my-todo/"
```

Or launch the full interactive TUI:

```bash
opencode --attach http://localhost:4096
```

---

## Troubleshooting

**`OpenCode CLI not found`**
```bash
npm install -g opencode-ai
# or
curl -fsSL https://opencode.ai/install | bash
```

**`local/qwen2.5-coder:7b not found in OpenCode`**
```bash
# Make sure LOCAL_ENDPOINT is exported in your shell
export LOCAL_ENDPOINT=http://localhost:11434/v1
# Then verify the model is pulled
ollama list
```

**`Ollama server not running`**
```bash
ollama serve
```

**`OpenCode server did not become healthy`**
- Check that port 4096 is free: `lsof -i :4096`
- Try a different port in `config.yaml`: `opencode_server_port: 4097`
- Check OpenCode logs: run `opencode serve` manually to see errors

**Agent produces no output / empty files**
- The model may be struggling with the prompt. Try a larger model:
  ```json
  "web-app-builder": { "model": "local/qwen2.5-coder:14b" }
  ```
- Increase `steps` in the agent config to allow more iterations
- Increase `max_loop_iterations` in `config.yaml`

**Out of VRAM (8GB)**
Switch to smaller models:
```json
{
  "agent": {
    "web-planner":     { "model": "local/qwen2.5-coder:3b" },
    "web-app-builder": { "model": "local/qwen2.5-coder:3b" },
    "web-reviewer":    { "model": "local/llama3.2:1b" },
    "web-writer":      { "model": "local/qwen2.5-coder:3b" }
  }
}
```

---

## Writing Good Prompts

The quality of the output scales directly with prompt quality. Use `.prompt.md` files for best results.

**Good prompt structure:**
```markdown
# App Title

One-sentence description.

## Features
- Specific feature 1 (be precise)
- Specific feature 2

## Design
Color scheme, fonts, layout style.

## Technical
Backend needed? Framework? Data persistence method?
Files to generate?
```

**Tips:**
- Name every feature explicitly — the agent only implements what you describe
- Specify the color scheme and design direction
- State whether localStorage, a backend, or no persistence is needed
- List the files you expect (`index.html`, `style.css`, `app.js`)

---

## License

MIT
