# AISocial Voice Agent - Product Roadmap

> Full roadmap from current state to production SaaS.
> Updated: February 2026

---

## Phase 1: Foundation (DONE)

- [x] Fork Google ADK samples repo
- [x] Create `aisocial-kit` branch
- [x] Build config-driven agent engine
- [x] Implement multi-agent architecture (root + sub-agents)
- [x] Create generic tool layer (webhook, notify, save_lead)
- [x] Build FastAPI HTTP server with REST API
- [x] Write pyproject.toml with all dependencies
- [x] Create .env.example template
- [x] Write comprehensive README
- [x] Write documentation (Guidelines, Architecture, New Bot Guide, Voice Plan)

---

## Phase 2: First Customer Bot

- [ ] Clone repo locally and test with Gemini API key
- [ ] Create first real client config (e.g., plumber, clinic)
- [ ] Test complete conversation flows end-to-end
- [ ] Add sample configs for 3-5 industries
- [ ] Fix any bugs found during testing
- [ ] Add input validation and error handling
- [ ] Deploy to Cloud Run or Railway for live testing

---

## Phase 3: Persistent Storage

- [ ] Replace in-memory lead store with Supabase/PostgreSQL
- [ ] Replace InMemorySessionService with Redis or DB-backed sessions
- [ ] Add lead export endpoint (CSV/JSON)
- [ ] Add conversation history storage
- [ ] Add basic analytics (leads per bot, conversations per day)

---

## Phase 4: Voice Integration

- [ ] Set up Twilio account and buy test number
- [ ] Build WebSocket handler for Twilio Media Streams
- [ ] Integrate Google STT for speech-to-text
- [ ] Integrate Google TTS for text-to-speech
- [ ] Test end-to-end voice call flow
- [ ] Map phone numbers to bot configs
- [ ] Add call recording/logging
- [ ] Optimize for low latency (<2s response time)

---

## Phase 5: Notifications & Integrations

- [ ] Implement SMS notifications via Twilio
- [ ] Implement WhatsApp notifications via Twilio/Meta API
- [ ] Implement email notifications (SendGrid/SMTP)
- [ ] Add Zapier webhook integration guide
- [ ] Add Google Calendar integration for bookings
- [ ] Add Calendly integration for appointments

---

## Phase 6: Bot Builder UI

- [ ] Build web UI for creating bot configs (no YAML editing)
- [ ] Form-based bot creation: name, industry, persona, goals
- [ ] Preview/test bot in browser before deploying
- [ ] One-click deployment of new bots
- [ ] Dashboard showing all active bots and their stats

---

## Phase 7: Multi-Language & Localization

- [ ] Add Arabic language support (RTL)
- [ ] Add Hindi language support
- [ ] Add multi-language STT/TTS for voice calls
- [ ] Per-bot language configuration
- [ ] Auto-detect caller language

---

## Phase 8: Production & Scaling

- [ ] Dockerize the application
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Deploy to Google Cloud Run (auto-scaling)
- [ ] Add rate limiting and authentication to API
- [ ] Add monitoring and alerting (Cloud Monitoring)
- [ ] Add per-customer usage tracking and billing
- [ ] Vertex AI Agent Engine deployment option

---

## Phase 9: Advanced Features

- [ ] Bot-that-builds-bots: ADK agent that generates YAML configs
- [ ] A/B testing for bot personas
- [ ] Conversation analytics and insights dashboard
- [ ] Custom voice cloning (ElevenLabs)
- [ ] Multi-model support (swap between Gemini, GPT, Claude)
- [ ] Agent evaluation and quality scoring
- [ ] Outbound calling capability

---

## Revenue Model Ideas

| Model | Description | Price Range |
|-------|-------------|-------------|
| Per-bot | Monthly fee per active bot | $29-99/month |
| Per-call | Charge per minute of voice calls | $0.10-0.30/min |
| Per-lead | Charge per captured lead | $1-5/lead |
| Setup fee | One-time bot configuration | $199-499 |
| Enterprise | Custom pricing for large clients | $500+/month |

---

## Tech Stack Summary

| Layer | Technology |
|-------|------------|
| AI Framework | Google ADK (Agent Development Kit) |
| LLM | Gemini 2.5 Flash |
| API Server | FastAPI + Uvicorn |
| Config | YAML files |
| Database | Supabase/PostgreSQL (planned) |
| Sessions | In-memory -> Redis (planned) |
| Telephony | Twilio (planned) |
| STT | Google STT (planned) |
| TTS | Google TTS / ElevenLabs (planned) |
| Deployment | Cloud Run / Railway |
| Frontend | React/Next.js (planned) |
| Repo | github.com/bibinsmart007/adk-samples |
