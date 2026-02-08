"""
Tools for the Transfer Agent — handles escalation to human support.
"""

from database import get_db


def request_human_transfer(reason: str, context: str = "", session_id: str = "") -> dict:
    """Request a transfer to a human support agent.

    Args:
        reason: The reason for requesting a human agent (e.g. complex issue, customer request).
        context: Summary of the conversation so far to hand off to the human agent. Optional.
        session_id: The current session ID for tracking. Optional.

    Returns:
        A dict with the transfer request status and queue position.
    """
    try:
        with get_db() as conn:
            cursor = conn.execute(
                """INSERT INTO transfer_queue (session_id, reason, context)
                   VALUES (?, ?, ?)""",
                (session_id, reason, context),
            )
            transfer_id = cursor.lastrowid

            # Get queue position
            row = conn.execute(
                "SELECT COUNT(*) as position FROM transfer_queue WHERE status = 'pending' AND id <= ?",
                (transfer_id,),
            ).fetchone()
            position = row["position"] if row else 1

        return {
            "status": "success",
            "transfer_id": transfer_id,
            "queue_position": position,
            "detail": (
                f"Transfer request #{transfer_id} created. "
                f"You are number {position} in the queue. "
                "A human agent will be with you shortly."
            ),
        }
    except Exception as e:
        return {"status": "error", "detail": f"Failed to request transfer: {str(e)}"}


def check_transfer_status(transfer_id: int) -> dict:
    """Check the status of a human transfer request.

    Args:
        transfer_id: The ID of the transfer request.

    Returns:
        A dict with the current transfer status.
    """
    try:
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM transfer_queue WHERE id = ?", (transfer_id,)
            ).fetchone()
        if not row:
            return {"status": "error", "detail": f"Transfer #{transfer_id} not found."}
        return {"status": "success", "transfer": dict(row)}
    except Exception as e:
        return {"status": "error", "detail": f"Failed to check status: {str(e)}"}
