# AISocial Voice Agent

**Config-driven AI agent engine built on Google ADK (Agent Development Kit)**

By [AISocialGrowth](https://aisocialgrowth.com) | Built by Bibin Lonappan

---

## What is this?

A reusable, config-driven AI agent that can be customized for **any business vertical** - plumber, clinic, agency, restaurant, etc. Built on top of Google's Agent Development Kit (ADK), it provides:

- **Multi-agent architecture**: Root agent + specialized sub-agents (lead intake, webhooks)
- **Config-driven behavior**: Change a YAML file to create a new bot personality
- **Generic tool layer**: Webhook calls, owner notifications, lead storage
- **HTTP API**: FastAPI server that any frontend or telephony system can use
- **ADK compatible**: Works with `adk run`, `adk web`, and Vertex AI deployment

## Architecture

```
aisocial-voice-agent/
|-- aisocial_voice_agent/         # Python package (ADK agent)
|   |-- __init__.py               # Package entry point
|   |-- agent.py                  # Root agent + sub-agents (ADK Agent class)
|   |-- config.py                 # YAML config loader with caching
|   |-- tools.py                  # Generic tools (webhook, notify, save_lead)
|   |-- configs/
|       |-- default.yaml           # Base bot config template
|-- server.py                     # FastAPI HTTP server
|-- pyproject.toml                # Dependencies and build config
|-- .env.example                  # Environment variable template
|-- README.md                     # This file
```

## Quick Start

### 1. Prerequisites

- Python 3.12+
- A Google API key (Gemini) from https://aistudio.google.com/apikey

### 2. Setup

```bash
# Navigate to the agent directory
cd python/agents/aisocial-voice-agent

# Copy environment template
cp .env.example .env

# Edit .env and add your GOOGLE_API_KEY

# Install dependencies
pip install -e .
```

### 3. Run with ADK CLI (recommended for development)

```bash
# Interactive terminal mode
adk run aisocial_voice_agent

# Web UI mode (opens browser)
adk web aisocial_voice_agent
```

### 4. Run with FastAPI server (for production / integration)

```bash
python server.py
```

Server starts at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/configs` | List available bot configs |
| GET | `/configs/{bot_id}` | Get specific bot config |
| POST | `/session` | Create new conversation session |
| POST | `/chat` | Send message and get reply |
| GET | `/leads` | Retrieve all saved leads |

### Example: Create session and chat

```bash
# Create a session
curl -X POST http://localhost:8000/session \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "default"}'

# Chat (use session_id from above)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "YOUR_SESSION_ID",
    "message": "Hi, I need to book a plumber"
  }'
```

## Creating a New Bot

1. Copy `aisocial_voice_agent/configs/default.yaml` to a new file:
   ```bash
   cp aisocial_voice_agent/configs/default.yaml aisocial_voice_agent/configs/plumber.yaml
   ```

2. Edit the new YAML with your business-specific values:
   - `bot_name`, `industry`, `persona`, `goals`, `tools`, `escalation_rules`

3. Use the new config:
   ```bash
   curl -X POST http://localhost:8000/session \
     -d '{"bot_id": "plumber"}'
   ```

That's it - no code changes needed for a new bot!

## Tools

| Tool | Description |
|------|-------------|
| `http_webhook` | POST JSON to any URL (CRM, Zapier, backend) |
| `notify_owner` | Alert business owner (log/email/SMS/WhatsApp stub) |
| `save_lead` | Save caller info with reference ID |

## Future Roadmap

- [ ] Voice integration (Twilio / LiveKit + STT/TTS)
- [ ] Supabase/PostgreSQL lead storage
- [ ] SMS/WhatsApp notifications via Twilio
- [ ] Bot Builder UI (generate configs from web form)
- [ ] Multi-language support
- [ ] Vertex AI deployment scripts
- [ ] Per-customer billing and usage tracking

## License

Apache License 2.0
