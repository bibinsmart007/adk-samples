# How to Create a New Bot

> Step-by-step guide for creating a new AI agent for any customer or business.
> No coding required - just create a YAML config file.

---

## Quick Version (3 steps)

1. Copy `default.yaml` to a new file
2. Edit the YAML with client details
3. Use the new `bot_id` when creating sessions

---

## Detailed Steps

### Step 1: Copy the default config

```bash
cd aisocial_voice_agent/configs/
cp default.yaml my_client.yaml
```

### Step 2: Edit the new config

Open `my_client.yaml` and customize:

```yaml
bot_id: "my_client"
bot_name: "My Client AI Assistant"
industry: "plumbing"   # or: clinic, restaurant, agency, etc.

persona: |
  You are a friendly and knowledgeable AI receptionist for
  ABC Plumbing Services in Abu Dhabi. You help callers book
  plumbing appointments, get emergency service, and answer
  common plumbing questions. You speak English and Arabic.

goals:
  - "Greet the caller and identify their plumbing need."
  - "Determine if it is an emergency or a scheduled appointment."
  - "Collect name, phone, address, and preferred time."
  - "For emergencies, notify the owner immediately."
  - "Confirm all details and provide a reference number."

tools:
  - "http_webhook"
  - "notify_owner"
  - "save_lead"

escalation_rules:
  transfer_to_human: true
  transfer_conditions:
    - "caller requests to speak with owner"
    - "emergency requiring immediate dispatch"
    - "pricing disputes or complaints"

language: "en"
max_turns: 20
webhook_url: "https://hooks.zapier.com/abc123"  # optional
notify_channel: "log"
```

### Step 3: Use the new bot

**With ADK CLI:**
The config is auto-loaded. Just test with messages.

**With HTTP API:**
```bash
# Create session with new bot
curl -X POST http://localhost:8000/session \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "my_client"}'

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SESSION_ID", "message": "I have a leaky pipe"}'
```

---

## Config Field Reference

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `bot_id` | Yes | Unique ID (matches filename) | `"plumber_uae"` |
| `bot_name` | Yes | Display name | `"ABC Plumbing AI"` |
| `industry` | Yes | Business vertical | `"plumbing"` |
| `persona` | Yes | Bot personality (multi-line) | See above |
| `goals` | Yes | List of objectives | See above |
| `tools` | Yes | Enabled tools | `["save_lead", "notify_owner"]` |
| `escalation_rules` | Yes | When to hand off | See above |
| `language` | No | Response language | `"en"`, `"ar"`, `"hi"` |
| `max_turns` | No | Max conversation turns | `20` |
| `webhook_url` | No | External webhook URL | `"https://..."` |
| `notify_channel` | No | How to notify owner | `"log"`, `"sms"`, `"email"` |

---

## Industry-Specific Tips

### Plumber / Electrician / Handyman
- Goals: Emergency detection, appointment booking, location collection
- Persona: Reassuring, understands urgency
- Escalation: Emergency situations

### Clinic / Doctor
- Goals: Symptom triage, appointment booking, insurance info
- Persona: Calm, professional, empathetic
- Escalation: Severe symptoms, prescription requests

### Restaurant
- Goals: Reservation booking, menu questions, delivery orders
- Persona: Friendly, knows the menu
- Escalation: Large group bookings, complaints

### Marketing Agency
- Goals: Lead qualification, service explanation, meeting booking
- Persona: Confident, sales-oriented
- Escalation: Budget discussions, custom proposals

### Real Estate
- Goals: Property inquiries, viewing bookings, price info
- Persona: Professional, detail-oriented
- Escalation: Negotiation, legal questions

---

## Adding Custom Tools (Advanced)

If a client needs a tool that does not exist:

1. Create a new file: `aisocial_voice_agent/tools_custom.py`
2. Write a function following the ADK pattern:
   ```python
   def book_appointment(
       name: str,
       date: str,
       time: str,
       service: str,
   ) -> dict:
       """Book an appointment for the caller.

       Args:
           name: Caller's name.
           date: Preferred date (YYYY-MM-DD).
           time: Preferred time (HH:MM).
           service: Type of service needed.
       Returns:
           Dict with booking confirmation.
       """
       # Your implementation here
       return {"status": "ok", "booking_id": "BK-001"}
   ```
3. Import and add the tool to agent.py
4. Add the tool name to the client's YAML config

Never modify the base `tools.py` for client-specific tools.

---

## Checklist for New Client Bot

- [ ] Config YAML created with unique `bot_id`
- [ ] Persona accurately reflects the business
- [ ] Goals cover the main use cases
- [ ] Escalation rules include edge cases
- [ ] Tested with ADK CLI (`adk run`)
- [ ] Tested with HTTP API (`POST /chat`)
- [ ] Webhook URL configured (if needed)
- [ ] Client approved the bot personality
