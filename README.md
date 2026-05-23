# Koan — Institutional Memory That Never Quits

> Your team's senior engineer that's been here since day one.

Koan is an AI agent that reads your GitHub repo's full engineering history — commits, merges, contributors, code structure — and builds a permanent, queryable institutional memory. It captures what the last engineer knew before they left: architecture decisions, risks, tribal knowledge, and who knows what.

Built on [GitAgent](https://github.com/open-gitagent/gitagent), the framework-agnostic, git-native standard for defining AI agents.

---

## The Problem

Organizational amnesia is the silent killer of engineering teams.

- A senior engineer leaves → months of "why did we build it this way?" with no answers
- An outage gets fixed at 3 AM → the context dies in a Slack thread nobody will find again
- A new hire joins → spends 2-3 months just learning unwritten rules and tribal knowledge
- Two teams merge → neither knows what the other learned the hard way

Confluence goes stale. Slack threads get buried. ChatGPT has no memory of your team. RAG over docs has no history, no "when did we learn this," and no correction mechanism.

**Koan fills the gap**: living, auditable, evolving, team-owned knowledge that accumulates passively and answers "why" — not just "what."

---

## How It Works

```
  GitHub Repo URL
        |
        v
  +-----+------+
  | Clone Repo  |  git clone + unshallow for full history
  +-----+------+
        |
        v
  +-----+---------+
  | Analyze Repo   |  README, deps, folders, key files
  |                |  + git log (100 commits)
  |                |  + merge commits (PR decisions)
  |                |  + contributor map (who knows what)
  |                |  + recently changed areas
  +-----+---------+
        |
        v
  +-----+-----------+
  | Extract Memory   |  LLM extracts institutional knowledge:
  |  (Gemini/Groq)   |  onboarding, architecture, decisions,
  |                   |  expertise map, risks, systems
  +-----+------------+
        |
        v
  +-----+-----------+
  | Build GitAgent   |  Generates agent.yaml, SOUL.md, RULES.md
  |                  |  Writes memory/ as markdown
  +-----+------------+
        |
        v
  +-----+------+
  | Query It   |  "Why does the payment service use idempotency keys?"
  |            |  → Answer with confidence + source citations
  +------------+
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for GitAgent CLI)
- Git
- A free LLM API key (Gemini or Groq)

### Setup

```bash
# Clone the project
git clone https://github.com/your-username/koan.git
cd koan/backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Install GitAgent CLI
npm install -g @shreyaskapale/gitagent

# Configure your LLM (pick one)
# Get a free Gemini key: https://aistudio.google.com/apikey
# Get a free Groq key:   https://console.groq.com/keys
echo GEMINI_API_KEY=your-key-here > .env

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-reload
```

### Generate Memory from a Repo

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/pallets/flask",
    "description": "Flask is a lightweight Python web framework maintained by the Pallets team."
  }'
```

### Query the Memory

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the biggest risks in this codebase?",
    "agent_path": "generated_agents/flask"
  }'
```

### Validate the Generated Agent

```bash
cd generated_agents/flask
gitagent validate
gitagent export --format system-prompt
```

---

## Project Structure

```
koan/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── api/
│   │   │   └── routes.py           # /generate and /ask endpoints
│   │   ├── services/
│   │   │   ├── llm.py              # Multi-provider LLM (Gemini > Groq > OpenAI > fallback)
│   │   │   ├── pipeline.py         # Orchestrates clone → analyze → generate → build
│   │   │   └── clone.py            # Git clone with Windows compatibility
│   │   ├── analyzers/
│   │   │   └── repo_analyzer.py    # Extracts code structure + git history
│   │   ├── generators/
│   │   │   ├── memory_generator.py # LLM-powered knowledge extraction
│   │   │   └── gitagent_generator.py  # Builds agent.yaml, SOUL.md, RULES.md
│   │   └── query/
│   │       └── ask.py              # Natural language query engine
│   ├── .env                        # API keys (not committed)
│   └── requirements.txt
├── frontend/                       # React dashboard (optional)
└── generated_agents/               # Output: one GitAgent per repo
    └── flask/
        ├── agent.yaml
        ├── SOUL.md
        ├── RULES.md
        └── memory/
            └── onboarding.md
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/generate` | Clone a repo, analyze it, generate institutional memory |
| `POST` | `/ask` | Query the generated memory with natural language |

### POST /generate

**Request:**
```json
{
  "repo_url": "https://github.com/pallets/flask",
  "description": "Flask web framework maintained by Pallets team"
}
```

**Response:**
```json
{
  "status": "success",
  "agent": "flask",
  "analysis": { ... },
  "memory": "## Onboarding Notes\n...",
  "agent_path": "generated_agents/flask"
}
```

### POST /ask

**Request:**
```json
{
  "question": "Who are the key contributors?",
  "agent_path": "generated_agents/flask"
}
```

**Response:**
```json
{
  "answer": "Based on the git history, the primary contributors are..."
}
```

---

## What Makes Koan Different

| Feature | Koan | Confluence | ChatGPT | RAG Bots |
|---------|------|------------|---------|----------|
| Learns from git history | Yes | No | No | No |
| Knows WHO knows what | Yes | No | No | No |
| Cites sources | Yes | N/A | No | Partial |
| Confidence levels | Yes | No | No | No |
| GitAgent-compatible | Yes | No | No | No |
| Exportable to any framework | Yes | No | No | No |
| Works offline (fallback) | Yes | No | No | No |

---

## GitAgent Integration

Every generated agent is a valid GitAgent repo:

- **`agent.yaml`** — Agent manifest with model config, skills, and compliance rules
- **`SOUL.md`** — Agent identity, communication style, and values
- **`RULES.md`** — Hard constraints (never hallucinate, always cite, strip PII)
- **`memory/`** — Extracted knowledge as markdown files

---

## Tech Stack

- **Backend:** Python, FastAPI, GitPython
- **LLM:** Google Gemini 2.0 Flash (free tier)
- **Agent Standard:** GitAgent v0.1.0
- **Memory Format:** Markdown, git-tracked

---
