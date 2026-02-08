"""
Tools for the Product Agent — searches and retrieves product information.
"""

from database import get_db


def search_products(query: str = "", category: str = "") -> dict:
    """Search products by keyword and/or category.

    Args:
        query: Search text to match against product name, description, and keywords. Optional.
        category: Filter by product category. Optional.

    Returns:
        A dict with matching products.
    """
    try:
        sql = "SELECT * FROM products WHERE in_stock = 1"
        params = []

        if query:
            search_term = f"%{query}%"
            sql += " AND (name LIKE ? OR description LIKE ? OR keywords LIKE ?)"
            params.extend([search_term, search_term, search_term])

        if category:
            sql += " AND category = ?"
            params.append(category)

        sql += " ORDER BY name"

        with get_db() as conn:
            rows = conn.execute(sql, params).fetchall()

        products = [dict(row) for row in rows]
        if not products:
            return {
                "status": "success",
                "count": 0,
                "products": [],
                "detail": "No products found matching your criteria. Try different search terms.",
            }
        return {"status": "success", "count": len(products), "products": products}
    except Exception as e:
        return {"status": "error", "detail": f"Failed to search products: {str(e)}"}


def get_product_details(product_id: int) -> dict:
    """Get detailed information about a specific product.

    Args:
        product_id: The ID of the product to retrieve.

    Returns:
        A dict with the full product details.
    """
    try:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()

        if not row:
            return {"status": "error", "detail": f"Product #{product_id} not found."}
        return {"status": "success", "product": dict(row)}
    except Exception as e:
        return {"status": "error", "detail": f"Failed to get product: {str(e)}"}


def list_product_categories() -> dict:
    """List all available product categories.

    Returns:
        A dict with a list of product categories and count per category.
    """
    try:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT category, COUNT(*) as count FROM products WHERE in_stock = 1 GROUP BY category ORDER BY category"
            ).fetchall()

        categories = [{"category": row["category"], "count": row["count"]} for row in rows]
        return {"status": "success", "categories": categories}
    except Exception as e:
        return {"status": "error", "detail": f"Failed to list categories: {str(e)}"}
