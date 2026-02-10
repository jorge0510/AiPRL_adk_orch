"""
Template rendering for dynamic agent instructions.
Replaces {{variable}} placeholders with values from session state and current time.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

CST_TZ = ZoneInfo("America/Chicago")


def render_instruction(template: str, state: dict) -> str:
    """Replace {{variable}} placeholders in an instruction template."""
    now_cst = datetime.now(CST_TZ)

    values = {
        "user_channel": state.get("user_channel", ""),
        "current_account_time": now_cst.strftime("%A, %B %d, %Y %I:%M %p CST"),
        "current_user_time": state.get(
            "current_user_time",
            now_cst.strftime("%A, %B %d, %Y %I:%M %p"),
        ),
        "full_name": state.get("full_name", ""),
        "email": state.get("email", ""),
        "phone": state.get("phone", ""),
        "chat_history": state.get("chat_history", ""),
        "Products and Promotions": state.get("Products and Promotions", ""),
        "Notices and Policies": state.get("Notices and Policies", ""),
        "Business Updates": state.get("Business Updates", ""),
    }

    result = template
    for key, value in values.items():
        result = result.replace("{{" + key + "}}", str(value))
    return result


def make_instruction_provider(template: str):
    """Return a callable instruction provider for Google ADK agents.

    Google ADK accepts instruction as a string or a callable.
    When callable, it receives an invocation context with access to session state.
    This function creates a callable that renders the template using session state.
    """
    def _provider(context) -> str:
        state = {}
        # Handle different context structures from ADK
        if hasattr(context, "state") and context.state:
            state = dict(context.state)
        elif hasattr(context, "session") and hasattr(context.session, "state"):
            state = dict(context.session.state)
        return render_instruction(template, state)

    return _provider
