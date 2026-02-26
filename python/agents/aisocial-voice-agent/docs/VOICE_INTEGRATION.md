# Voice & Telephony Integration Plan

> How to make our ADK agent answer real phone calls.
> This is the future integration layer - our ADK engine stays the same.

---

## Overview

To make an AI bot that answers phone calls, we need 3 additional layers
on top of our existing ADK agent:

1. **Telephony** - Receives/makes calls (Twilio, Vonage, Asterisk)
2. **STT** - Speech-to-Text (converts caller audio to text)
3. **TTS** - Text-to-Speech (converts agent reply to audio)

Our ADK engine remains unchanged - it receives text and returns text.
The voice gateway handles the audio conversion.

---

## Architecture: Phone Call Flow

```
Caller dials number
       |
       v
+------------------+
| Twilio / Vonage  |  <-- Telephony provider
| (receives call)  |      Manages SIP/PSTN
+--------+---------+
         |
    Audio stream
         |
+--------v---------+
| STT Service      |  <-- Google STT / Deepgram / AssemblyAI
| (audio -> text)  |
+--------+---------+
         |
    Text message
         |
+--------v---------+
| Our ADK Engine   |  <-- POST /chat (existing API)
| (text -> reply)  |      No changes needed!
+--------+---------+
         |
    Reply text
         |
+--------v---------+
| TTS Service      |  <-- Google TTS / ElevenLabs / Azure TTS
| (text -> audio)  |
+--------+---------+
         |
    Audio stream
         |
+--------v---------+
| Twilio / Vonage  |
| (plays to caller)|  --> Caller hears response
+------------------+
```

---

## Option 1: Twilio + Media Streams (Recommended to start)

### How it works
- Buy a Twilio phone number
- Configure webhook to point to our server
- Twilio streams audio via WebSocket
- We process with STT, send to ADK, return TTS audio

### Cost estimate
- Twilio number: ~$1/month
- Twilio per-minute: ~$0.013/min inbound
- Google STT: ~$0.006/15 seconds
- Google TTS: Free tier available
- Gemini: ~$0.001-0.01 per turn
- **Total per 5-min call: ~$0.15-0.25**

### Implementation steps
1. Get Twilio account and phone number
2. Create a WebSocket handler in server.py
3. Integrate Google STT streaming API
4. Pipe transcribed text to `POST /chat`
5. Convert reply to speech with Google TTS
6. Stream audio back to Twilio

---

## Option 2: LiveKit Agents (More advanced)

### How it works
- LiveKit provides a real-time voice agent framework
- Built-in STT/TTS pipeline
- We plug our ADK agent as the LLM backend
- Supports WebRTC for low latency

### Best for
- Very low latency requirements
- Web-based voice (browser calls)
- Multi-modal (voice + screen sharing)

---

## Option 3: Bland.ai / Vapi / Retell (Fastest to ship)

### How it works
- SaaS platforms that handle telephony + STT + TTS
- We provide our API endpoint as the "brain"
- They call POST /chat for each turn
- Minimal code needed

### Best for
- Quick proof of concept
- Client demos
- Small-scale deployments

---

## STT Provider Comparison

| Provider | Latency | Cost | Languages | Best for |
|----------|---------|------|-----------|----------|
| Google STT | Low | $0.006/15s | 125+ | Multi-language, accuracy |
| Deepgram | Very low | $0.0043/min | 30+ | Speed, English |
| AssemblyAI | Low | $0.01/min | 10+ | Accuracy, diarization |
| OpenAI Whisper | Medium | $0.006/min | 100+ | Cost, accuracy |

## TTS Provider Comparison

| Provider | Quality | Cost | Voices | Best for |
|----------|---------|------|--------|----------|
| Google TTS | Good | Free tier | 200+ | Budget, multilingual |
| ElevenLabs | Excellent | $0.18/1K chars | Custom | Natural voice |
| Azure TTS | Great | $4/1M chars | 400+ | Enterprise |
| OpenAI TTS | Great | $15/1M chars | 6 | Simple, good quality |

---

## Per-Customer Phone Setup

For each new client who wants phone calls:

1. Buy a Twilio number for their region
2. Point the number's webhook to our server
3. Create their bot config YAML
4. Map the phone number to their `bot_id`
5. Test with a real call

---

## Implementation Priority

1. **Phase 1**: Text chat working (DONE)
2. **Phase 2**: Twilio basic voice (next)
3. **Phase 3**: Low-latency streaming STT/TTS
4. **Phase 4**: Multi-language voice
5. **Phase 5**: LiveKit for web-based voice
