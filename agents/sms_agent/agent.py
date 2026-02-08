"""
SMS Agent — handles sending SMS messages via Telnyx.
"""

from google.adk.agents import Agent
from .tools import send_sms

sms_agent = Agent(
    name="sms_agent",
    model="gemini-2.0-flash",
    description="Sends SMS text messages to phone numbers using the Telnyx API.",
    instruction="""You are the SMS Agent. Your job is to send SMS text messages.

When a user wants to send an SMS:
1. Make sure you have the recipient phone number in E.164 format (e.g. +12125551234).
2. Make sure you have the message content.
3. If either is missing, ask the user to provide it.
4. Call the send_sms tool with the phone number and message.
5. Report the result back to the user.

Always confirm the phone number and message before sending.
Do NOT send messages without explicit user confirmation of the content.""",
    tools=[send_sms],
)
