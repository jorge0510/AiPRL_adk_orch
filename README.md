# Madison — Patty Peck Honda AI Assistant

AI-powered customer service REST API for **Patty Peck Honda** built with [Google ADK](https://google.github.io/adk-docs/) and [FastAPI](https://fastapi.tiangolo.com/). A root orchestrator ("Madison") powered by Gemini 2.0 Flash intelligently routes customer requests to 7 specialized agents.

## Architecture

```
Client ──► POST /chat ──► FastAPI ──► ADK Runner ──► Orchestrator ("Madison")
                                                        │
               ┌────────────┬────────────┬──────────────┼──────────────┬────────────┬────────────┐
               ▼            ▼            ▼              ▼              ▼            ▼            ▼
           Booking       Ticket        SMS           Maps           FAQ        Product      Transfer
            Agent         Agent       Agent          Agent          Agent        Agent        Agent
               │            │            │              │              │            │            │
            SQLite       SQLite      Telnyx API   Google Maps      SQLite       SQLite       SQLite
```

Agent instructions are rendered dynamically each turn using `template_utils.py`, which injects session state values (user name, email, phone, current time in CST) into `{{variable}}` placeholders.

## Agents

| Agent | What It Does |
|-------|-------------|
| **Orchestrator** | "Madison" — analyzes intent, provides Patty Peck Honda info, and delegates to the right sub-agent |
| **Booking Agent** | Book, list, and cancel appointments (in-person car visits only, not service) |
| **Ticket Agent** | Create, view, update, and list support tickets (used outside working hours) |
| **SMS Agent** | Send text messages via Telnyx v4 |
| **Maps Agent** | Get directions and map links via Google Maps |
| **FAQ Agent** | Search a knowledge base of frequently asked questions |
| **Product Agent** | Search products, browse categories, get product details |
| **Transfer Agent** | Escalate to a human agent (only during working hours) |

## Working Hours (CST)

- Mon: 8:30 AM - 7:00 PM
- Tue - Sat: 8:30 AM - 8:00 PM
- Sun: Closed
- Holiday closures: Thanksgiving, Christmas Day, New Year's Day; Christmas Eve closes at 2 PM

During working hours, users can be transferred to a human agent. Outside working hours, the system creates a support ticket instead.

## Prerequisites

- Python 3.10+
- API keys for:
  - [Google Gemini](https://ai.google.dev/) (required — key starts with `AIza...`)
  - [Telnyx](https://telnyx.com/) (required for SMS agent — key starts with `KEY...`)
  - [Google Maps Platform](https://developers.google.com/maps) (required for Maps agent)

## Setup

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and fill in your API keys:

   ```
   GOOGLE_API_KEY=your-gemini-api-key
   TELNYX_API_KEY=your-telnyx-api-key
   TELNYX_PHONE_NUMBER=+1XXXXXXXXXX
   GOOGLE_MAPS_API_KEY=your-google-maps-api-key
   ```

3. **Seed the database** (optional — loads sample FAQs and products)

   ```bash
   python seed_data.py
   ```

4. **Start the server**

   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## API Endpoints

### Health Check

```
GET /health
```

Returns `{"status": "ok"}`.

### Create Session

```
POST /sessions
Content-Type: application/json

{
  "user_id": "default_user",
  "context": {
    "user_channel": "web",
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+16015551234"
  }
}
```

Creates a new conversation session with optional user context. The `context` fields are stored in session state and injected into agent instructions via the template system. All fields are optional.

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Session created successfully."
}
```

### Get Session History

```
GET /sessions/{session_id}?user_id=default_user
```

Retrieves the conversation history for a session.

### Chat

```
POST /chat
Content-Type: application/json

{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "I'd like to book an appointment for tomorrow at 2pm",
  "context": {
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+16015551234"
  }
}
```

Sends a message to the orchestrator and returns the agent's response. The optional `context` updates session state for the current and future turns.

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "I'd be happy to help you book an appointment! ...",
  "events": [...]
}
```

## Example Conversations

```
User: "What are your hours?"
→ Orchestrator answers directly from its business knowledge

User: "I want to come see a car tomorrow at 2pm"
→ Routed to Booking Agent → collects info one-by-one → books appointment

User: "I need to talk to someone"
→ (during hours) Routed to Transfer Agent → collects info → transfers to human
→ (outside hours) Routed to Ticket Agent → collects info → creates support ticket

User: "How do I get to the dealership from downtown Jackson?"
→ Routed to Maps Agent → fetches directions via Google Maps API

User: "Send a text to +16015551234 saying my appointment is confirmed"
→ Routed to SMS Agent → sends SMS via Telnyx

User: "What financing options do you have?"
→ Orchestrator answers directly (Patty Peck Honda finance info)
```

## Project Structure

```
v3/
├── main.py                    # FastAPI app, endpoints, ADK runner, session state
├── template_utils.py          # {{variable}} template rendering for agent instructions
├── database.py                # SQLite connection and schema
├── seed_data.py               # Sample data seeder
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
├── .gitignore
├── CLAUDE.md                  # Coding conventions and architecture notes
│
└── agents/
    ├── orchestrator/
    │   └── agent.py           # Root agent "Madison" with Patty Peck Honda context
    ├── booking_agent/
    │   ├── agent.py           # Appointment booking (in-person car visits only)
    │   └── tools.py           # book, list, cancel appointments
    ├── ticket_agent/
    │   ├── agent.py           # Support tickets (outside working hours)
    │   └── tools.py           # create, get, list, update tickets
    ├── sms_agent/
    │   ├── agent.py
    │   └── tools.py           # send SMS via Telnyx v4 client API
    ├── maps_agent/
    │   ├── agent.py
    │   └── tools.py           # directions and map links via Google Maps
    ├── faq_agent/
    │   ├── agent.py
    │   └── tools.py           # search FAQs by keyword/category
    ├── product_agent/
    │   ├── agent.py
    │   └── tools.py           # search products, details, categories
    └── transfer_agent/
        ├── agent.py           # Human transfer (working hours only)
        └── tools.py           # request transfer, check queue status
```

## Template System

Agent instructions use `{{variable}}` placeholders that are rendered per-turn from session state:

| Variable | Source |
|----------|--------|
| `{{current_account_time}}` | Computed each turn (`America/Chicago` timezone) |
| `{{current_user_time}}` | Session state or defaults to CST |
| `{{full_name}}` | Session state (from `UserContext`) |
| `{{email}}` | Session state (from `UserContext`) |
| `{{phone}}` | Session state (from `UserContext`) |
| `{{user_channel}}` | Session state (from `UserContext`) |

This is powered by `make_instruction_provider()` in `template_utils.py`, which returns a callable that ADK invokes on each turn with the current invocation context.

## Database

SQLite database (`app.db`) with 5 tables, auto-created on startup:

- **appointments** — customer appointments with date, time, service type, status
- **tickets** — support tickets with priority, status, category
- **transfer_queue** — human escalation requests with queue position tracking
- **faqs** — knowledge base entries with keyword search
- **products** — product catalog with category, price, stock status

## Tech Stack

- [Google ADK](https://google.github.io/adk-docs/) + Gemini 2.0 Flash
- [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- [SQLite](https://www.sqlite.org/) (via `sqlite3` + `aiosqlite`)
- [Telnyx v4](https://telnyx.com/) (SMS)
- [Google Maps Platform](https://developers.google.com/maps) (Directions)
- [Pydantic](https://docs.pydantic.dev/) (validation)
- [python-dotenv](https://github.com/theskumar/python-dotenv) (configuration)
- [tzdata](https://pypi.org/project/tzdata/) (Windows timezone support)
