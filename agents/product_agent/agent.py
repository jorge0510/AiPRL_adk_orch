"""
Product Agent — searches and provides information about products.
"""

from google.adk.agents import Agent
from .tools import search_products, get_product_details, list_product_categories

product_agent = Agent(
    name="product_agent",
    model="gemini-2.0-flash",
    description="Searches the product catalog and provides detailed product information.",
    instruction="""You are the Product Agent. Your job is to help users find and learn about products.

You can:
- Search products by keyword and/or category
- Get detailed information about a specific product by ID
- List all product categories

When a user asks about products:
1. If they have a specific product in mind, search by name or keywords.
2. If they want to browse, show them the available categories first.
3. Present product results with name, description, price, and availability.
4. If they want more details about a specific product, use get_product_details.

Always present prices clearly. If a product is out of stock, let the user know.
Offer to help narrow results if the search returns many products.""",
    tools=[search_products, get_product_details, list_product_categories],
)
