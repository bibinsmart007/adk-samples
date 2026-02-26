# AISocial Voice Agent - Architecture

> System architecture, layer design, and how all components connect.

---

## High-Level Architecture

```
+-----------------------------------------------------------+
|                    CLIENT LAYER                            |
|  Web Frontend | WhatsApp Bot | Twilio Voice | Mobile App  |
+----------------------------+------------------------------+
                             |
                      HTTP REST API
                             |
+----------------------------v------------------------------+
|                   SERVER LAYER (server.py)                 |
|  FastAPI + Pydantic models                                |
|  Endpoints: /session, /chat, /configs, /leads             |
+----------------------------+------------------------------+
                             |
+----------------------------v------------------------------+
|                   ADK ENGINE LAYER                         |
|  Google ADK Runner + InMemorySessionService               |
|  Manages: sessions, conversation state, agent routing     |
+----------------------------+------------------------------+
                             |
+----------------------------v------------------------------+
|                   AGENT LAYER (agent.py)                   |
|                                                           |
|  root_agent (orchestrator)                                |
|    |-- lead_intake_agent (collects leads)                 |
|    |-- webhook_agent (external integrations)              |
|    |-- [future] booking_agent                             |
|    |-- [future] support_agent                             |
+----------------------------+------------------------------+
                             |
+----------------------------v------------------------------+
|                   TOOL LAYER (tools.py)                    |
|  http_webhook | notify_owner | save_lead | get_leads      |
|  [future] book_appointment | query_crm | send_sms         |
+----------------------------+------------------------------+
                             |
+----------------------------v------------------------------+
|                   CONFIG LAYER (config.py + configs/)      |
|  YAML configs per bot: persona, goals, tools, escalation  |
|  Caching + env var overrides                              |
+-----------------------------------------------------------+
```

---

## Layer Responsibilities

### 1. Client Layer

Anything that talks to our API. We do NOT build this layer yet.
Examples:
- Web chat widget (React/Next.js)
- Twilio voice gateway (audio -> STT -> our API -> TTS -> audio)
- WhatsApp Business API bot
- Mobile app SDK

### 2. Server Layer (`server.py`)

- FastAPI app exposing REST endpoints
- Request/response validation via Pydantic
- Session management (create, lookup)
- Delegates all AI logic to the ADK Engine Layer
- Stateless (sessions stored in session service)

### 3. ADK Engine Layer

- Google ADK `Runner` handles agent execution
- `InMemorySessionService` manages conversation state
- Handles multi-turn conversations automatically
- Routes messages to the correct agent/sub-agent
- For production: swap to persistent session store

### 4. Agent Layer (`agent.py`)

- `root_agent`: Main orchestrator. Greets users, understands intent,
  delegates to sub-agents.
- `lead_intake_agent`: Specialized in collecting contact info and
  saving leads.
- `webhook_agent`: Sends data to external systems via HTTP.
- All agents use `gemini-2.5-flash` model.
- Instructions come from config (via `build_system_prompt`).

### 5. Tool Layer (`tools.py`)

- Plain Python functions with typed args and docstrings.
- ADK reads docstrings to generate tool descriptions for the LLM.
- Tools are synchronous (ADK handles async wrapping).
- In-memory lead store for development; swap to DB for production.

### 6. Config Layer (`config.py` + `configs/`)

- YAML files define bot behavior (no code changes needed).
- `config.py` loads, caches, and validates configs.
- Environment variables can override config values.
- `build_system_prompt()` converts config to an LLM instruction string.

---

## Data Flow: Chat Message

```
1. Client sends POST /chat {session_id, message}
2. server.py validates request, creates Content object
3. Runner.run_async() is called with session_id + message
4. ADK routes to root_agent
5. root_agent reads message, decides action:
   a. Direct response -> returns reply
   b. Needs lead info -> delegates to lead_intake_agent
   c. Needs webhook -> delegates to webhook_agent
6. Sub-agent executes, may call tools (save_lead, etc.)
7. Sub-agent transfers back to root_agent
8. Final response sent back through Runner
9. server.py returns ChatResponse {reply, events}
```

---

## Future: Voice Call Architecture

```
+------------------+     +------------------+     +------------------+
|  Phone Network   | --> |  Twilio/LiveKit   | --> |  STT (Speech     |
|  (PSTN/SIP)      |     |  (Telephony)      |     |  to Text)        |
+------------------+     +------------------+     +--------+---------+
                                                           |
                                                    Text message
                                                           |
                                                  +--------v---------+
                                                  |  Our ADK Engine   |
                                                  |  POST /chat       |
                                                  +--------+---------+
                                                           |
                                                     Reply text
                                                           |
                                                  +--------v---------+
                                                  |  TTS (Text to     |
                                                  |  Speech)           |
                                                  +--------+---------+
                                                           |
                                                      Audio back
                                                           |
                                                  +--------v---------+
                                                  |  Twilio/LiveKit    |
                                                  |  -> Caller hears   |
                                                  +-------------------+
```

Key point: Our ADK engine stays the same. We only add a
telephony gateway + STT/TTS layer on top.

---

## Scaling Strategy

| Stage | Sessions | Architecture |
|-------|----------|-------------|
| Dev | In-memory | Single server, `adk web` or `server.py` |
| MVP | Redis | Single Cloud Run instance + Redis |
| Growth | PostgreSQL | Multiple Cloud Run instances + shared DB |
| Scale | Vertex AI | Vertex AI Agent Engine (managed) |

---

## Key Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Framework | Google ADK | Multi-agent, tool-native, model-agnostic |
| LLM | Gemini 2.5 Flash | Cost-effective, fast, good tool calling |
| Config format | YAML | Human-readable, easy to edit, no code needed |
| API framework | FastAPI | Async, fast, auto-docs, Pydantic validation |
| Session store | InMemory (dev) | Simple; swap to Redis/DB for production |
| Tool style | Plain functions | ADK pattern; docstrings = tool descriptions |
