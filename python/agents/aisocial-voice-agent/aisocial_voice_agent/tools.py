# Copyright 2025 AISocialGrowth
#
# AISocial Voice Agent - Tool Definitions
# Generic tools that can be used by any bot configuration.
# These are plain Python functions that ADK agents can call.

import json
import logging
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory lead store (replace with DB in production)
# ---------------------------------------------------------------------------
_lead_store: list[dict] = []


def http_webhook(
    payload: dict,
    url: str = "",
) -> dict:
    """Send a JSON payload to the specified webhook URL.

    Use this tool to push collected lead data or event notifications
    to external systems like CRMs, Zapier, or custom backends.

    Args:
        payload: The JSON data to send.
        url: The destination webhook URL.

    Returns:
        A dict with status and response code.
    """
    if not url:
        logger.warning("http_webhook called with empty URL; skipping.")
        return {"status": "skipped", "reason": "No webhook URL configured."}

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(url, json=payload)
        logger.info("Webhook POST %s -> %s", url, resp.status_code)
        return {"status": "ok", "code": resp.status_code}
    except Exception as e:
        logger.exception("Webhook POST failed")
        return {"status": "error", "error": str(e)}


def notify_owner(
    message: str,
    channel: str = "log",
) -> dict:
    """Notify the business owner about an important event.

    Use this tool when you need to alert the business owner,
    for example when a new lead is captured or when a caller
    needs to be transferred to a human.

    Args:
        message: The notification message text.
        channel: The notification channel (log, email, sms, whatsapp).

    Returns:
        A dict with status.
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    if channel == "log":
        logger.info("[OWNER NOTIFICATION] %s | %s", timestamp, message)
        return {"status": "ok", "channel": "log", "timestamp": timestamp}

    # Placeholder for future integrations
    # elif channel == "email":
    #     send_email(to=owner_email, subject="New Alert", body=message)
    # elif channel == "sms":
    #     send_sms(to=owner_phone, body=message)
    # elif channel == "whatsapp":
    #     send_whatsapp(to=owner_phone, body=message)

    logger.info(
        "[OWNER NOTIFICATION][%s] %s | %s",
        channel,
        timestamp,
        message,
    )
    return {"status": "ok", "channel": channel, "timestamp": timestamp}


def save_lead(
    name: str,
    phone: str = "",
    email: str = "",
    request_type: str = "general",
    details: str = "",
) -> dict:
    """Save a collected lead to the database.

    Use this tool after you have collected the caller's information
    and confirmed the details with them.

    Args:
        name: The caller's full name.
        phone: The caller's phone number.
        email: The caller's email address.
        request_type: Type of request (inquiry, booking, complaint, other).
        details: Additional details about the request.

    Returns:
        A dict with the saved lead info and a reference ID.
    """
    lead_id = f"LEAD-{len(_lead_store) + 1:04d}"
    timestamp = datetime.now(timezone.utc).isoformat()

    lead = {
        "lead_id": lead_id,
        "name": name,
        "phone": phone,
        "email": email,
        "request_type": request_type,
        "details": details,
        "created_at": timestamp,
    }

    _lead_store.append(lead)
    logger.info("Lead saved: %s", json.dumps(lead))

    return {
        "status": "ok",
        "lead_id": lead_id,
        "message": f"Lead {lead_id} saved successfully.",
    }


def get_leads() -> dict:
    """Retrieve all saved leads.

    Returns:
        A dict containing the list of all leads.
    """
    return {"status": "ok", "leads": _lead_store, "count": len(_lead_store)}
