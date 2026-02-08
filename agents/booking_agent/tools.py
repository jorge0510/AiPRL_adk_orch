"""
Tools for the Booking Agent — manages appointment scheduling via SQLite.
"""

from database import get_db


def book_appointment(
    customer_name: str,
    appointment_date: str,
    appointment_time: str,
    service_type: str,
    customer_email: str = "",
    customer_phone: str = "",
    notes: str = "",
) -> dict:
    """Book a new appointment.

    Args:
        customer_name: Full name of the customer.
        appointment_date: Date of the appointment in YYYY-MM-DD format.
        appointment_time: Time of the appointment in HH:MM format (24h).
        service_type: Type of service requested (e.g. consultation, repair, demo).
        customer_email: Customer email address (optional).
        customer_phone: Customer phone number (optional).
        notes: Additional notes for the appointment (optional).

    Returns:
        A dict with the booking status and appointment details.
    """
    try:
        with get_db() as conn:
            cursor = conn.execute(
                """INSERT INTO appointments
                   (customer_name, customer_email, customer_phone,
                    appointment_date, appointment_time, service_type, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (customer_name, customer_email, customer_phone,
                 appointment_date, appointment_time, service_type, notes),
            )
            appointment_id = cursor.lastrowid
        return {
            "status": "success",
            "appointment_id": appointment_id,
            "detail": f"Appointment booked for {customer_name} on {appointment_date} at {appointment_time}.",
        }
    except Exception as e:
        return {"status": "error", "detail": f"Failed to book appointment: {str(e)}"}


def list_appointments(
    customer_name: str = "",
    date: str = "",
    status: str = "scheduled",
) -> dict:
    """List appointments, optionally filtered by customer name, date, or status.

    Args:
        customer_name: Filter by customer name (partial match). Empty string means no filter.
        date: Filter by appointment date (YYYY-MM-DD). Empty string means no filter.
        status: Filter by status (scheduled, completed, cancelled). Defaults to scheduled.

    Returns:
        A dict with a list of matching appointments.
    """
    try:
        query = "SELECT * FROM appointments WHERE 1=1"
        params = []

        if customer_name:
            query += " AND customer_name LIKE ?"
            params.append(f"%{customer_name}%")
        if date:
            query += " AND appointment_date = ?"
            params.append(date)
        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY appointment_date, appointment_time"

        with get_db() as conn:
            rows = conn.execute(query, params).fetchall()

        appointments = [dict(row) for row in rows]
        return {
            "status": "success",
            "count": len(appointments),
            "appointments": appointments,
        }
    except Exception as e:
        return {"status": "error", "detail": f"Failed to list appointments: {str(e)}"}


def cancel_appointment(appointment_id: int) -> dict:
    """Cancel an existing appointment by its ID.

    Args:
        appointment_id: The ID of the appointment to cancel.

    Returns:
        A dict with the cancellation status.
    """
    try:
        with get_db() as conn:
            result = conn.execute(
                "UPDATE appointments SET status = 'cancelled', updated_at = datetime('now') WHERE id = ? AND status = 'scheduled'",
                (appointment_id,),
            )
            if result.rowcount == 0:
                return {
                    "status": "error",
                    "detail": f"Appointment {appointment_id} not found or already cancelled.",
                }
        return {
            "status": "success",
            "detail": f"Appointment {appointment_id} has been cancelled.",
        }
    except Exception as e:
        return {"status": "error", "detail": f"Failed to cancel appointment: {str(e)}"}
