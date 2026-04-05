# Multi-Agent CrewAI System 🤖

A CrewAI-based multi-agent pipeline that automatically analyzes any GitHub repository and generates a structured, detailed README — by understanding the codebase's architecture, flow, and features using LLMs.

---

## How It Works

Given a GitHub repository URL, the system:

1. **Fetches** the repository's file tree and source code via the GitHub API
2. **Passes** the extracted data through a sequential crew of four specialized AI agents
3. **Outputs** a polished `README_generated.md` file written entirely by the agents

### Agent Pipeline

| Agent | Role |
|---|---|
| `repo_explorer` | Navigates the repo structure and maps out file relationships |
| `system_analyzer` | Understands the code flow, architecture, and core features |
| `content_writer` | Drafts the README content based on the analysis |
| `formatter` | Structures and polishes the final markdown output |

### Task Flow

```
explore_task → analyze_task → write_task → format_task → README_generated.md
```

---

## Repository Structure

```
Multi-Agent-CrewAI-system/
├── main.py              # Entry point — orchestrates the crew
├── agents.py            # Agent definitions (roles, goals, backstories)
├── tasks.py             # Task definitions for each agent
├── github_utils.py      # GitHub API fetching & repo data extraction
├── check_models.py      # Utility to verify available LLM models
├── test_repo.py         # Test script for repo extraction
├── requirements.txt     # Python dependencies
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- An OpenAI (or compatible) API key for the LLM backend
- Internet access to reach the GitHub API

### Installation

```bash
git clone https://github.com/bhaumik694/Multi-Agent-CrewAI-system.git
cd Multi-Agent-CrewAI-system
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key
```

### Run

You can pass a GitHub URL as a command-line argument:

```bash
python main.py https://github.com/username/repository
```

Or run interactively (the script will prompt you):

```bash
python main.py
# Enter GitHub repo URL: https://github.com/username/repository
```

The generated README is saved as `README_generated.md` in the project root.

---

## GitHub Utility Details

`github_utils.py` handles all repository data extraction with a smart prioritization strategy:

- **README first** — always fetched for high-level context
- **Priority files** — entry points and core files (`main`, `app`, `server`, `index`, `api`, `routes`, `controllers`, etc.) are fetched next
- **Fallback sampling** — if too few files are found, a broader sample is taken
- **Hard limits** — token-efficient content slicing and a file cap keep LLM context manageable
- **Ignored paths** — `node_modules`, `dist`, `build`, `__pycache__`, `.git` are automatically excluded

Supported file types: `.py`, `.js`, `.ts`, `.tsx`, `.jsx`, `.json`, `.md`, `.yaml`, `.yml`

---

## Tech Stack

| Library | Purpose |
|---|---|
| [CrewAI](https://github.com/joaomdmoura/crewAI) | Multi-agent orchestration framework |
| [OpenAI / LLM](https://platform.openai.com/) | Language model backend for agents |
| [requests](https://docs.python-requests.org/) | GitHub API communication |

