"""
Tools for the FAQ Agent — searches and retrieves frequently asked questions.
"""

from database import get_db


def search_faq(query: str) -> dict:
    """Search FAQs by keyword matching in questions, answers, and keywords.

    Args:
        query: Search query string to match against FAQ content.

    Returns:
        A dict with matching FAQ entries.
    """
    try:
        search_term = f"%{query}%"
        with get_db() as conn:
            rows = conn.execute(
                """SELECT * FROM faqs
                   WHERE question LIKE ? OR answer LIKE ? OR keywords LIKE ?
                   ORDER BY id""",
                (search_term, search_term, search_term),
            ).fetchall()

        faqs = [dict(row) for row in rows]
        if not faqs:
            return {
                "status": "success",
                "count": 0,
                "faqs": [],
                "detail": f"No FAQs found matching '{query}'. Try different keywords.",
            }
        return {"status": "success", "count": len(faqs), "faqs": faqs}
    except Exception as e:
        return {"status": "error", "detail": f"Failed to search FAQs: {str(e)}"}


def list_faq_categories() -> dict:
    """List all available FAQ categories.

    Returns:
        A dict with a list of FAQ categories and the count per category.
    """
    try:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT category, COUNT(*) as count FROM faqs GROUP BY category ORDER BY category"
            ).fetchall()

        categories = [{"category": row["category"], "count": row["count"]} for row in rows]
        return {"status": "success", "categories": categories}
    except Exception as e:
        return {"status": "error", "detail": f"Failed to list categories: {str(e)}"}


def get_faqs_by_category(category: str) -> dict:
    """Get all FAQs in a specific category.

    Args:
        category: The FAQ category to retrieve.

    Returns:
        A dict with all FAQs in the specified category.
    """
    try:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM faqs WHERE category = ? ORDER BY id",
                (category,),
            ).fetchall()

        faqs = [dict(row) for row in rows]
        if not faqs:
            return {
                "status": "success",
                "count": 0,
                "faqs": [],
                "detail": f"No FAQs found in category '{category}'.",
            }
        return {"status": "success", "count": len(faqs), "faqs": faqs}
    except Exception as e:
        return {"status": "error", "detail": f"Failed to get FAQs: {str(e)}"}
