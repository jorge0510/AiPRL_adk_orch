"""
Tools for the SMS Agent — sends SMS messages via the Telnyx API.
"""

import os
import telnyx


def send_sms(to: str, message: str) -> dict:
    """Send an SMS message to a phone number.

    Args:
        to: The recipient phone number in E.164 format (e.g. +12125551234).
        message: The text message body to send.

    Returns:
        A dict with the send status and message_id.
    """
    api_key = os.getenv("TELNYX_API_KEY")
    from_number = os.getenv("TELNYX_PHONE_NUMBER")

    if not api_key:
        return {"status": "error", "detail": "TELNYX_API_KEY is not configured."}
    if not from_number:
        return {"status": "error", "detail": "TELNYX_PHONE_NUMBER is not configured."}

    try:
        client = telnyx.Telnyx(api_key=api_key)
        response = client.messages.send(
            from_=from_number,
            to=to,
            text=message,
        )
        return {
            "status": "success",
            "message_id": response.data.id,
            "to": to,
            "detail": f"SMS sent successfully to {to}.",
        }
    except telnyx.TelnyxError as e:
        return {
            "status": "error",
            "detail": f"Failed to send SMS: {str(e)}",
        }
