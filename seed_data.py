"""
Seed data script — populates the database with sample FAQs and products
so the system is usable out of the box.
"""

from database import init_db, get_db


def seed_faqs():
    """Insert sample FAQ entries."""
    faqs = [
        # Shipping
        ("What are the shipping options?",
         "We offer Standard (5-7 business days), Express (2-3 business days), and Overnight shipping. Free standard shipping on orders over $50.",
         "Shipping", "shipping,delivery,options,free"),
        ("How can I track my order?",
         "Once your order ships, you'll receive a tracking email with a link to track your package. You can also check your order status in your account dashboard.",
         "Shipping", "track,order,status,package"),
        ("Do you ship internationally?",
         "Yes! We ship to over 50 countries. International shipping rates and delivery times vary by destination. Check our shipping page for details.",
         "Shipping", "international,worldwide,global,overseas"),

        # Returns
        ("What is your return policy?",
         "We accept returns within 30 days of purchase. Items must be unused and in original packaging. Return shipping is free for defective items.",
         "Returns", "return,refund,policy,exchange"),
        ("How do I initiate a return?",
         "Go to your order history, select the item, and click 'Return Item'. You'll receive a prepaid shipping label via email within 24 hours.",
         "Returns", "return,initiate,start,process"),

        # Account
        ("How do I reset my password?",
         "Click 'Forgot Password' on the login page, enter your email, and follow the reset link sent to your inbox. The link expires in 24 hours.",
         "Account", "password,reset,forgot,login"),
        ("How do I update my payment method?",
         "Go to Account Settings > Payment Methods. You can add, remove, or update credit cards and other payment options.",
         "Account", "payment,credit card,billing,update"),

        # General
        ("What are your business hours?",
         "Our customer service team is available Monday-Friday 9AM-6PM EST. Chat support is available 24/7.",
         "General", "hours,business,support,contact,available"),
        ("How do I contact customer support?",
         "You can reach us via: Chat (24/7), Email: support@example.com, Phone: 1-800-555-0123 (Mon-Fri 9AM-6PM EST).",
         "General", "contact,support,email,phone,chat"),
        ("Do you have a loyalty program?",
         "Yes! Join our rewards program for free. Earn 1 point per $1 spent. 100 points = $5 off. Members get early access to sales and exclusive offers.",
         "General", "loyalty,rewards,program,points,membership"),

        # Technical
        ("Which browsers are supported?",
         "Our website works best with the latest versions of Chrome, Firefox, Safari, and Edge. We recommend keeping your browser updated for the best experience.",
         "Technical", "browser,supported,chrome,firefox,safari"),
        ("Is my data secure?",
         "Absolutely. We use industry-standard SSL encryption, and we never store your full credit card number. We are SOC 2 Type II certified.",
         "Technical", "security,data,privacy,encryption,safe"),
    ]

    with get_db() as conn:
        conn.execute("DELETE FROM faqs")  # Clear existing
        conn.executemany(
            "INSERT INTO faqs (question, answer, category, keywords) VALUES (?, ?, ?, ?)",
            faqs,
        )
    print(f"  Inserted {len(faqs)} FAQs.")


def seed_products():
    """Insert sample product entries."""
    products = [
        # Electronics
        ("Wireless Bluetooth Headphones",
         "Premium noise-cancelling wireless headphones with 30-hour battery life, comfortable over-ear design, and crystal-clear sound quality.",
         "Electronics", 79.99, 1, "WBH-001", None,
         "headphones,bluetooth,wireless,audio,music,noise-cancelling"),
        ("Smart Home Hub",
         "Central smart home controller compatible with Alexa, Google Home, and HomeKit. Controls lights, thermostats, locks, and more.",
         "Electronics", 129.99, 1, "SHH-001", None,
         "smart home,hub,controller,alexa,google,homekit"),
        ("Portable Charger 20000mAh",
         "High-capacity portable power bank with dual USB-C ports. Fast charges phones and tablets. Compact and lightweight design.",
         "Electronics", 39.99, 1, "PC-001", None,
         "charger,portable,power bank,battery,usb-c"),
        ("4K Webcam Pro",
         "Ultra HD 4K webcam with auto-focus, built-in ring light, and noise-cancelling microphone. Perfect for video calls and streaming.",
         "Electronics", 89.99, 1, "WC4K-001", None,
         "webcam,camera,4k,video,streaming,meetings"),

        # Accessories
        ("Laptop Stand - Aluminum",
         "Ergonomic aluminum laptop stand with adjustable height. Improves posture and airflow. Supports laptops up to 17 inches.",
         "Accessories", 49.99, 1, "LS-001", None,
         "laptop,stand,ergonomic,aluminum,desk"),
        ("Mechanical Keyboard RGB",
         "Full-size mechanical keyboard with customizable RGB backlighting, Cherry MX switches, and programmable macro keys.",
         "Accessories", 119.99, 1, "MK-001", None,
         "keyboard,mechanical,rgb,gaming,typing"),
        ("Wireless Mouse - Ergonomic",
         "Ergonomic vertical wireless mouse designed to reduce wrist strain. 6 buttons, adjustable DPI, and long battery life.",
         "Accessories", 34.99, 1, "WM-001", None,
         "mouse,wireless,ergonomic,vertical"),

        # Software
        ("Cloud Storage Plan - 1TB",
         "1TB cloud storage with automatic backup, file sync across devices, and secure sharing. Annual subscription.",
         "Software", 99.99, 1, "CS-1TB", None,
         "cloud,storage,backup,subscription"),
        ("VPN Premium - Annual",
         "Premium VPN service with unlimited bandwidth, 100+ server locations, and no-log policy. Protects up to 5 devices.",
         "Software", 59.99, 1, "VPN-001", None,
         "vpn,security,privacy,subscription"),

        # Office
        ("Desk Organizer Set",
         "5-piece desk organizer set including pen holder, document tray, memo pad holder, cable organizer, and drawer organizer.",
         "Office", 29.99, 1, "DO-001", None,
         "desk,organizer,office,tidy,storage"),
        ("Noise Machine - White Noise",
         "Desktop white noise machine with 20 soothing sounds. Timer function, adjustable volume, and compact design for better focus.",
         "Office", 44.99, 1, "NM-001", None,
         "noise machine,white noise,focus,sleep,relaxation"),
    ]

    with get_db() as conn:
        conn.execute("DELETE FROM products")  # Clear existing
        conn.executemany(
            "INSERT INTO products (name, description, category, price, in_stock, sku, image_url, keywords) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            products,
        )
    print(f"  Inserted {len(products)} products.")


def main():
    print("Initializing database...")
    init_db()
    print("Seeding data...")
    seed_faqs()
    seed_products()
    print("Done! Database is ready.")


if __name__ == "__main__":
    main()
