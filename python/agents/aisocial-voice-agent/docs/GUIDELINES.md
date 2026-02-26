# AISocial Voice Agent - Development Guidelines

> This document captures the full strategy, design decisions, and guidelines
> for developing AI agents using our ADK kit. Refer to this whenever you
> need to build, extend, or deploy a new agent.

---

## 1. Why Google ADK?

We chose Google ADK (Agent Development Kit) as our core framework because:

- **Multi-agent native**: Built for multi-agent workflows, tool calling, and
  structured state from the ground up.
- **Model-agnostic**: Optimized for Gemini/Vertex but designed to work with
  multiple LLMs (GPT, Claude, etc.) so we are not locked in.
- **Production-focused**: Built-in evaluation, observability, and clean
  deployment path to Cloud Run and Vertex AI Agent Engine.
- **Open-source and low-level**: Like LEGO bricks - we get fine control over
  workflows and state, perfect for building our own platform abstractions.
- **Google ecosystem**: Best integration with Gemini, Vertex AI, Cloud Run,
  and Google Cloud services.

### Tradeoffs to keep in mind

- ADK adds complexity vs a simple function+tools setup.
- Ecosystem is newer than LangChain/LangGraph but Google is pushing it hard.
- Best value when leaning into Google Cloud stack.

---

## 2. Core Principles

### Config-driven, not code-driven

Every new bot should be created by adding a YAML config file, NOT by writing
new Python code. The config controls:
- Bot personality (persona)
- Business goals
- Available tools
- Escalation rules
- Language

### Multi-agent architecture

Use sub-agents for specialized tasks:
- `lead_intake_agent` - collects and saves lead info
- `webhook_agent` - sends data to external systems
- Future: `booking_agent`, `support_agent`, `billing_agent`, etc.

The root_agent orchestrates and delegates to sub-agents.

### Tool layer is generic

Tools should be reusable across all bots:
- `http_webhook` - POST to any URL
- `notify_owner` - alert business owner
- `save_lead` - store lead data
- Future: `book_appointment`, `query_crm`, `send_sms`, etc.

Custom tools for specific clients go in separate files, never modify
the base tools.

### HTTP API as the integration surface

The FastAPI server is the single integration point. Any system
(web frontend, Twilio, LiveKit, WhatsApp bot) talks to our agent
through the same REST API:
- `POST /session` - start a conversation
- `POST /chat` - send a message
- `GET /leads` - retrieve saved leads

---

## 3. Project Structure

```
aisocial-voice-agent/
|-- aisocial_voice_agent/         # Python package (ADK agent)
|   |-- __init__.py               # Package entry
|   |-- agent.py                  # Root agent + sub-agents
|   |-- config.py                 # YAML config loader
|   |-- tools.py                  # Generic tools
|   |-- configs/
|       |-- default.yaml          # Base config template
|       |-- plumber.yaml          # Example: plumber bot
|       |-- clinic.yaml           # Example: clinic bot
|-- docs/                         # Documentation
|   |-- GUIDELINES.md             # This file
|   |-- ARCHITECTURE.md           # Architecture decisions
|   |-- NEW_BOT_GUIDE.md          # How to create new bots
|   |-- VOICE_INTEGRATION.md      # Voice/telephony plan
|   |-- ROADMAP.md                # Product roadmap
|-- server.py                     # FastAPI HTTP server
|-- pyproject.toml                # Dependencies
|-- .env.example                  # Environment template
|-- README.md                     # Quick start guide
```

---

## 4. ADK Patterns We Follow

### Agent Definition Pattern

We follow the exact ADK pattern used in Google's official samples:

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="root_agent",          # ADK looks for this name
    model="gemini-2.5-flash",   # Default model
    global_instruction="...",   # Always-on context
    instruction="...",          # Task-specific instructions
    sub_agents=[...],           # Specialized sub-agents
    tools=[...],                # Available tools
)
```

### Tool Definition Pattern

Tools are plain Python functions with docstrings (ADK reads them):

```python
def save_lead(
    name: str,
    phone: str = "",
    email: str = "",
    request_type: str = "general",
    details: str = "",
) -> dict:
    """Save a collected lead to the database.

    Use this tool after collecting caller info.

    Args:
        name: Caller's full name.
        phone: Phone number.
        ...
    Returns:
        Dict with lead_id and status.
    """
    # implementation
```

The docstring is critical - ADK uses it to tell the LLM when/how
to call the tool.

### Session and Runner Pattern

For the HTTP server, we use ADK's Runner and InMemorySessionService:

```python
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="aisocial_voice_agent",
    session_service=session_service,
)
```

For production, replace InMemorySessionService with a persistent
store (Redis, PostgreSQL, Firestore).

---

## 5. Config Format Reference

Every bot config YAML must have these fields:

```yaml
bot_id: "unique-id"              # Unique identifier
bot_name: "Display Name"         # Human-readable name
industry: "vertical"             # Business vertical

persona: |                       # Multi-line personality
  You are a friendly ...

goals:                           # List of objectives
  - "Goal 1"
  - "Goal 2"

tools:                           # Which tools to enable
  - "http_webhook"
  - "notify_owner"
  - "save_lead"

escalation_rules:                # When to hand off
  transfer_to_human: true
  transfer_conditions:
    - "condition 1"
    - "condition 2"

language: "en"                   # Response language
max_turns: 25                    # Max conversation turns
webhook_url: ""                  # External webhook
notify_channel: "log"            # Notification method
```

---

## 6. Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Gemini API key |
| `GOOGLE_CLOUD_PROJECT` | No | For Vertex AI deployment |
| `GOOGLE_CLOUD_LOCATION` | No | Cloud region |
| `AISOCIAL_WEBHOOK_URL` | No | Default webhook URL |
| `AISOCIAL_NOTIFY_CHANNEL` | No | Notification channel |
| `SERVER_HOST` | No | Server bind host (default 0.0.0.0) |
| `SERVER_PORT` | No | Server port (default 8000) |

Env vars override config values. This lets you deploy the same
code with different settings per environment.

---

## 7. Development Workflow

### Adding a new feature

1. Always work on the `aisocial-kit` branch (or a feature branch off it).
2. Follow the existing patterns - check how similar agents/tools work.
3. Add tests if possible.
4. Update relevant docs in `docs/`.

### Testing locally

```bash
# Terminal mode (quick test)
adk run aisocial_voice_agent

# Web UI mode (visual test)
adk web aisocial_voice_agent

# HTTP API mode (integration test)
python server.py
# Then use curl or Postman against localhost:8000
```

### Deployment options

1. **Cloud Run** - Containerize and deploy FastAPI server.
2. **Vertex AI Agent Engine** - Use ADK's built-in deployment.
3. **Railway/Render** - Simple PaaS deployment.
4. **Self-hosted** - Run on any VPS with Python 3.12+.

---

## 8. Security Guidelines

- **Never commit `.env` files** - only `.env.example`.
- **API keys in env vars only** - never hardcode.
- **Validate webhook URLs** - only allow known domains.
- **Rate limit the API** - add middleware in server.py.
- **Sanitize user input** - the LLM handles most, but validate
  tool inputs too.

---

## 9. Cost Optimization

- Use `gemini-2.5-flash` (not Pro) for sub-agents - cheaper and faster.
- Set `max_turns` in config to prevent runaway conversations.
- Cache configs (already done in config.py).
- Use in-memory session store for development, persistent for production.
- Monitor token usage per session via ADK observability.

---

## 10. Key Commands Reference

```bash
# Install
cd python/agents/aisocial-voice-agent
pip install -e .

# Run with ADK CLI
adk run aisocial_voice_agent
adk web aisocial_voice_agent

# Run HTTP server
python server.py

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/configs
curl -X POST http://localhost:8000/session -H "Content-Type: application/json" -d '{"bot_id": "default"}'
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"session_id": "ID", "message": "hello"}'
```
