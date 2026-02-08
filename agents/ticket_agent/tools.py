"""
Tools for the Ticket Agent — manages support tickets via SQLite.
"""

from database import get_db


def create_ticket(
    customer_name: str,
    subject: str,
    description: str,
    priority: str = "medium",
    category: str = "",
    customer_email: str = "",
) -> dict:
    """Create a new support ticket.

    Args:
        customer_name: Full name of the customer.
        subject: Brief subject/title of the issue.
        description: Detailed description of the issue.
        priority: Ticket priority — low, medium, high, or urgent. Defaults to medium.
        category: Ticket category (e.g. billing, technical, general). Optional.
        customer_email: Customer email address. Optional.

    Returns:
        A dict with the ticket creation status and ticket details.
    """
    if priority not in ("low", "medium", "high", "urgent"):
        return {"status": "error", "detail": f"Invalid priority '{priority}'. Must be low, medium, high, or urgent."}

    try:
        with get_db() as conn:
            cursor = conn.execute(
                """INSERT INTO tickets
                   (customer_name, customer_email, subject, description, priority, category)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (customer_name, customer_email, subject, description, priority, category),
            )
            ticket_id = cursor.lastrowid
        return {
            "status": "success",
            "ticket_id": ticket_id,
            "detail": f"Support ticket #{ticket_id} created: '{subject}' (priority: {priority}).",
        }
    except Exception as e:
        return {"status": "error", "detail": f"Failed to create ticket: {str(e)}"}


def get_ticket(ticket_id: int) -> dict:
    """Get details of a specific support ticket.

    Args:
        ticket_id: The ID of the ticket to retrieve.

    Returns:
        A dict with the ticket details.
    """
    try:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if not row:
            return {"status": "error", "detail": f"Ticket #{ticket_id} not found."}
        return {"status": "success", "ticket": dict(row)}
    except Exception as e:
        return {"status": "error", "detail": f"Failed to get ticket: {str(e)}"}


def list_tickets(
    customer_name: str = "",
    status: str = "",
    priority: str = "",
) -> dict:
    """List support tickets with optional filters.

    Args:
        customer_name: Filter by customer name (partial match). Empty string means no filter.
        status: Filter by status (open, in_progress, resolved, closed). Empty string means no filter.
        priority: Filter by priority (low, medium, high, urgent). Empty string means no filter.

    Returns:
        A dict with a list of matching tickets.
    """
    try:
        query = "SELECT * FROM tickets WHERE 1=1"
        params = []

        if customer_name:
            query += " AND customer_name LIKE ?"
            params.append(f"%{customer_name}%")
        if status:
            query += " AND status = ?"
            params.append(status)
        if priority:
            query += " AND priority = ?"
            params.append(priority)

        query += " ORDER BY created_at DESC"

        with get_db() as conn:
            rows = conn.execute(query, params).fetchall()

        tickets = [dict(row) for row in rows]
        return {"status": "success", "count": len(tickets), "tickets": tickets}
    except Exception as e:
        return {"status": "error", "detail": f"Failed to list tickets: {str(e)}"}


def update_ticket(
    ticket_id: int,
    status: str = "",
    priority: str = "",
    category: str = "",
) -> dict:
    """Update an existing support ticket.

    Args:
        ticket_id: The ID of the ticket to update.
        status: New status (open, in_progress, resolved, closed). Empty string means no change.
        priority: New priority (low, medium, high, urgent). Empty string means no change.
        category: New category. Empty string means no change.

    Returns:
        A dict with the update status.
    """
    updates = []
    params = []

    if status:
        if status not in ("open", "in_progress", "resolved", "closed"):
            return {"status": "error", "detail": f"Invalid status '{status}'."}
        updates.append("status = ?")
        params.append(status)
    if priority:
        if priority not in ("low", "medium", "high", "urgent"):
            return {"status": "error", "detail": f"Invalid priority '{priority}'."}
        updates.append("priority = ?")
        params.append(priority)
    if category:
        updates.append("category = ?")
        params.append(category)

    if not updates:
        return {"status": "error", "detail": "No fields to update."}

    updates.append("updated_at = datetime('now')")
    params.append(ticket_id)

    try:
        with get_db() as conn:
            result = conn.execute(
                f"UPDATE tickets SET {', '.join(updates)} WHERE id = ?",
                params,
            )
            if result.rowcount == 0:
                return {"status": "error", "detail": f"Ticket #{ticket_id} not found."}
        return {
            "status": "success",
            "detail": f"Ticket #{ticket_id} updated successfully.",
        }
    except Exception as e:
        return {"status": "error", "detail": f"Failed to update ticket: {str(e)}"}
