# CLAUDE.md — Project Guidelines for AI Assistants

## Project Overview

Multi-Agent Customer Service API for **Patty Peck Honda**, built with Google ADK and FastAPI. A root orchestrator agent ("Madison") routes requests to 7 specialized sub-agents. Agent instructions use dynamic template rendering with session state for per-user context (channel, name, email, phone, current time in CST).

## Tech Stack

- **Python 3.11+**
- **Google ADK** (`google-adk`) — agent framework using Gemini 2.0 Flash
- **FastAPI** + **Uvicorn** — REST API server on port 8000
- **SQLite** — persistent storage (WAL mode, foreign keys enabled)
- **Telnyx v4** — SMS delivery (client-based API, `telnyx.Telnyx()`)
- **Google Maps API** — directions/navigation (external API)
- **Pydantic** — request/response validation
- **zoneinfo** + **tzdata** — CST timezone handling for template rendering

## Architecture

```
main.py (FastAPI)
  ├── template_utils.py (instruction template rendering)
  └── Runner(root_agent)
        └── agents/orchestrator/agent.py ("Madison" — Patty Peck Honda)
              ├── agents/booking_agent/    (appointments, in-person visits only)
              ├── agents/ticket_agent/     (support tickets, outside working hours)
              ├── agents/transfer_agent/   (human escalation, during working hours)
              ├── agents/sms_agent/        (SMS via Telnyx v4)
              ├── agents/maps_agent/       (directions via Google Maps)
              ├── agents/faq_agent/        (knowledge base search)
              └── agents/product_agent/    (product catalog)
```

- **Orchestrator** delegates to sub-agents; it never handles tasks directly.
- Each sub-agent lives in `agents/<name>/` with `agent.py` (definition) and `tools.py` (callable functions).
- Database access is centralized in `database.py`.
- Template rendering is centralized in `template_utils.py`.

## Template System

Agent instructions contain `{{variable}}` placeholders that are rendered dynamically per-turn via `make_instruction_provider()`.

### Supported Variables

| Variable | Source | Example |
|----------|--------|---------|
| `{{current_account_time}}` | Auto-computed (CST) | `Monday, February 10, 2026 02:30 PM CST` |
| `{{current_user_time}}` | Session state or CST fallback | `Monday, February 10, 2026 02:30 PM` |
| `{{user_channel}}` | Session state | `Webchat`, `Instagram`, `Facebook`, `SMS` |
| `{{full_name}}` | Session state | `John Doe` |
| `{{email}}` | Session state | `john@example.com` |
| `{{phone}}` | Session state | `+15551234567` |

### How It Works

1. `template_utils.make_instruction_provider(template)` returns a callable
2. ADK calls this callable on each turn with the invocation context
3. The callable reads session state and renders `{{variables}}` with live values
4. `{{current_account_time}}` is always computed fresh in CST timezone

### Adding New Template Variables

1. Add the variable to `render_instruction()` in `template_utils.py`
2. Use `{{variable_name}}` in agent instruction templates
3. Pass the value via session state (set in `context` on session creation or chat requests)

## Coding Conventions

### File Structure

- Each agent has its own directory: `agents/<agent_name>/`
- `agent.py` — defines `INSTRUCTION_TEMPLATE` string and `Agent` instance
- `tools.py` — defines plain Python functions that the agent can call
- All agents import from `google.adk.agents.Agent`
- Agents with template variables import `make_instruction_provider` from `template_utils`
- Tools import `get_db` from `database` for DB access

### Agent Definition Pattern (with templates)

```python
from google.adk.agents import Agent
from .tools import tool_a, tool_b
from template_utils import make_instruction_provider

INSTRUCTION_TEMPLATE = """You are the Some Agent...
Current Time: {{current_account_time}}
User Name: {{full_name}}
..."""

some_agent = Agent(
    name="some_agent",           # snake_case, matches directory name
    model="gemini-2.0-flash",    # all agents use this model
    description="...",           # one-line summary for the orchestrator
    instruction=make_instruction_provider(INSTRUCTION_TEMPLATE),
    tools=[tool_a, tool_b],      # list of tool functions
)
```

### Agent Definition Pattern (static, no templates)

```python
from google.adk.agents import Agent
from .tools import tool_a, tool_b

some_agent = Agent(
    name="some_agent",
    model="gemini-2.0-flash",
    description="...",
    instruction="""Static instruction string...""",
    tools=[tool_a, tool_b],
)
```

### Tool Function Pattern

- Plain functions (not classes), fully type-hinted parameters and `-> dict` return
- Google-style docstrings with `Args:` and `Returns:` sections (ADK uses these for the LLM)
- Always return a dict with `"status": "success"` or `"status": "error"` plus `"detail"` message
- On success, include relevant data keys (`appointment_id`, `ticket`, `products`, etc.)
- Wrap DB/API calls in try/except, returning error dicts instead of raising
- Use `get_db()` context manager for all database operations
- Use parameterized queries (`?` placeholders) — never interpolate user input into SQL

```python
def some_tool(required_arg: str, optional_arg: str = "") -> dict:
    """Brief description.

    Args:
        required_arg: What this argument is.
        optional_arg: What this argument is. Optional.

    Returns:
        A dict with the result status and relevant data.
    """
    try:
        with get_db() as conn:
            # parameterized query
            conn.execute("... WHERE col = ?", (required_arg,))
        return {"status": "success", "detail": "..."}
    except Exception as e:
        return {"status": "error", "detail": f"Failed to ...: {str(e)}"}
```

### External API Tool Pattern (Telnyx v4 example)

```python
import telnyx

client = telnyx.Telnyx(api_key=api_key)
response = client.messages.send(from_=from_number, to=to, text=message)
# Access response data via response.data.id
# Catch errors with telnyx.TelnyxError
```

### Database Conventions

- All schema lives in `database.py` → `init_db()`
- Tables use `CREATE TABLE IF NOT EXISTS`
- Timestamp columns: `created_at` and `updated_at` with `DEFAULT (datetime('now'))`
- Status columns: string-based enums (e.g. `scheduled`/`completed`/`cancelled`)
- Connections use `sqlite3.Row` row factory for dict-like access
- Updates set `updated_at = datetime('now')` explicitly
- Dynamic query building uses `WHERE 1=1` + conditional `AND` clauses with parameterized values

### API Conventions (main.py)

- Pydantic `BaseModel` for all request/response schemas
- `UserContext` model for passing user info (`user_channel`, `full_name`, `email`, `phone`)
- Context can be set on session creation (`CreateSessionRequest.context`) or per-chat (`ChatRequest.context`)
- Context is stored in ADK session state and persists across messages
- Endpoints raise `HTTPException` for client errors (404 for missing sessions)
- Session IDs are UUID4 strings
- All endpoints are async
- All session service calls must use `await` (ADK v1.0+ async API)
- FastAPI lifespan hook initializes the database on startup

### Naming Conventions

- **Agents**: `snake_case` names matching their directory (e.g. `booking_agent`)
- **Tools**: `snake_case` verb-noun functions (e.g. `book_appointment`, `search_products`)
- **Files**: lowercase, underscores (e.g. `seed_data.py`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g. `APP_NAME`, `DB_PATH`, `INSTRUCTION_TEMPLATE`)
- **Module docstrings**: every `.py` file starts with a triple-quoted docstring

### Environment & Configuration

- API keys loaded via `python-dotenv` from `.env` (never committed — see `.gitignore`)
- Template in `.env.example`
- Tools that need external API keys check for them at call time and return error dicts if missing
- `DATABASE_PATH` env var overrides the default `app.db`

## Running the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Fill in your API keys in .env

# Seed the database (optional — populates FAQs and products)
python seed_data.py

# Start the server
python main.py
# or: uvicorn main:app --reload
```

## Adding a New Agent

1. Create `agents/<new_agent>/agent.py` and `agents/<new_agent>/tools.py`
2. Define tool functions in `tools.py` following the tool pattern above
3. Define `INSTRUCTION_TEMPLATE` and the `Agent` in `agent.py`:
   - If the agent needs dynamic context, use `make_instruction_provider(INSTRUCTION_TEMPLATE)`
   - If static instructions suffice, use a plain string
4. Register it in `agents/orchestrator/agent.py`:
   - Import the agent
   - Add it to `sub_agents=[]`
   - Add routing guidance to the orchestrator's `INSTRUCTION_TEMPLATE`
5. If the agent needs new DB tables, add them to `init_db()` in `database.py`
6. If new template variables are needed, add them to `template_utils.py`

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app, endpoints, ADK runner, session state management |
| `template_utils.py` | Dynamic instruction template rendering with `{{variables}}` |
| `database.py` | SQLite connection, schema initialization |
| `seed_data.py` | Sample FAQ and product data |
| `agents/orchestrator/agent.py` | Root agent ("Madison") with Patty Peck Honda context |
| `agents/*/agent.py` | Sub-agent definitions with instruction templates |
| `agents/*/tools.py` | Tool functions for each sub-agent |
| `.env.example` | Required environment variables template |

## Business Context

This system is configured for **Patty Peck Honda** (555 Sunnybrook Rd, Ridgeland, MS 39157). The orchestrator contains full business info (hours, contacts, services, loyalty programs, finance options). All working hours are in CST. The assistant persona is named "Madison".

Key routing rules:
- Appointments are ONLY for in-person car visits, not service
- Service scheduling redirects to the website
- Human transfer only during sales hours; outside hours → ticket creation
- Never provide price estimates; direct to vehicle pages instead
