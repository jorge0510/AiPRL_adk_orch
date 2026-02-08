"""
Transfer Agent — handles escalation to human support agents.
"""

from google.adk.agents import Agent
from .tools import request_human_transfer, check_transfer_status

transfer_agent = Agent(
    name="transfer_agent",
    model="gemini-2.0-flash",
    description="Transfers the conversation to a human support agent when needed.",
    instruction="""You are the Human Transfer Agent. Your job is to handle requests to speak with a human.

When a user wants to talk to a human agent:
1. Ask for the reason they need a human (if not already clear from context).
2. Summarize the conversation so far as context for the human agent.
3. Call request_human_transfer with the reason and context.
4. Inform the user of their queue position and that a human will be with them shortly.

You can also check the status of an existing transfer request if the user asks.

Be empathetic and reassuring. Let the user know their concern is important and will be handled by a real person.""",
    tools=[request_human_transfer, check_transfer_status],
)
