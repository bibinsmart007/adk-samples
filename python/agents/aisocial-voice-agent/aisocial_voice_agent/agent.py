# Copyright 2025 AISocialGrowth
#
# AISocial Voice Agent - Core Agent Definition
# Uses Google ADK Agent class with config-driven behavior.
# This is the main agent that handles all conversations.

from google.adk.agents import Agent

from .config import build_system_prompt, load_bot_config
from .tools import http_webhook, notify_owner, save_lead

# ---------------------------------------------------------------------------
# Load default config and build the system prompt
# ---------------------------------------------------------------------------
_default_config = load_bot_config("default")
_system_prompt = build_system_prompt(_default_config)

# ---------------------------------------------------------------------------
# Lead Intake Sub-Agent
# Specialized in collecting and saving lead information
# ---------------------------------------------------------------------------
lead_intake_agent = Agent(
    name="lead_intake_agent",
    model="gemini-2.5-flash",
    description="Collects and saves lead information from callers",
    instruction="""You are a specialized lead intake assistant.
    Your job is to collect contact information and request details from callers.

    Steps:
    - Do not greet the user (the main agent already did).
    - Collect the caller's full name.
    - Collect their phone number.
    - Collect their email address (optional but encouraged).
    - Ask about the type of request: inquiry, booking, complaint, or other.
    - Collect specific details about their request.
    - Repeat the collected information back as bullet points and ask for confirmation.
    - If confirmed, use the `save_lead` tool to save the lead.
    - Tell them their reference ID and that someone will follow up.
    - Use the `notify_owner` tool to alert the business owner.
    - Transfer back to the parent agent without saying anything else.""",
    tools=[save_lead, notify_owner],
)

# ---------------------------------------------------------------------------
# Webhook Sub-Agent
# Specialized in sending data to external systems
# ---------------------------------------------------------------------------
webhook_agent = Agent(
    name="webhook_agent",
    model="gemini-2.5-flash",
    description="Sends data to external webhooks and integrations",
    instruction="""You are a specialized integration assistant.
    Your job is to send collected data to external systems via webhooks.

    Steps:
    - Do not greet the user.
    - Confirm what data needs to be sent.
    - Use the `http_webhook` tool to send the data.
    - Report the result back.
    - Transfer back to the parent agent without saying anything else.""",
    tools=[http_webhook],
)

# ---------------------------------------------------------------------------
# Root Agent - The main conversational agent
# This is what ADK looks for (must be named root_agent)
# ---------------------------------------------------------------------------
root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    global_instruction=f"""You are {_default_config.get('bot_name', 'AISocial Business Agent')},
    a professional AI assistant powered by AISocialGrowth.
    Always respond politely and professionally.
    Industry: {_default_config.get('industry', 'generic')}.""",
    instruction=f"""{_system_prompt}

    You are the main customer service assistant. Your job is to help
    callers with their requests efficiently and professionally.

    Steps:
    - Welcome the caller warmly. Introduce yourself as the business assistant.
    - Ask how you can help them today.
    - Listen carefully to understand their need.
    - If they need to provide contact details or make a request,
      delegate to the lead_intake_agent.
    - If they need data sent to an external system,
      delegate to the webhook_agent.
    - After the user's request has been handled, ask if there's anything else.
    - When done, thank them warmly and end the conversation.

    Important:
    - If the user asks for a human or you cannot help after 3 attempts,
      use the notify_owner tool to escalate.
    - Always be concise but thorough.
    - Never make up information you don't have.""",
    sub_agents=[lead_intake_agent, webhook_agent],
    tools=[notify_owner, save_lead],
)
