from storage import get_connection
from cart import get_cart, clear_cart
from products import get_product
from datetime import datetime


def setup_discount_codes():
    # Add default discount codes
    conn = get_connection()
    cursor = conn.cursor()

    codes = [("SAVE10", 10, 1), ("SAVE15", 15, 1), ("SAVE20", 20, 1)]

    for code, percent, active in codes:
        cursor.execute(
            "INSERT OR IGNORE INTO discount_codes (code, percent, active) VALUES (?, ?, ?)",
            (code, percent, active),
        )

    conn.commit()
    conn.close()


def check_discount_code(code):
    if not code:
        return None

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT code, percent, active FROM discount_codes WHERE code = ?",
        (code.upper(),),
    )
    row = cursor.fetchone()
    conn.close()

    if row and row["active"] == 1:
        return {"code": row["code"], "percent": row["percent"]}
    return None


def checkout(username, discount_code=None):
    # get cart
    items, total = get_cart(username)
    if len(items) == 0:
        return False, "Your cart is empty.", None

    # check stock again before placing order
    for item in items:
        product = get_product(item["product_id"])
        if not product:
            return False, "Product no longer available.", None
        if item["qty"] > product["stock"]:
            return False, "Not enough stock for " + product["name"], None

    # apply discount if code is valid
    discount_amount = 0
    applied_code = None
    discount = check_discount_code(discount_code)

    if discount:
        discount_amount = total * (discount["percent"] / 100)
        applied_code = discount["code"]

    final_total = total - discount_amount
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # save order in db
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO orders (username, total_price, discount_code, discount_amount, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (username, final_total, applied_code, discount_amount, "PAID", timestamp),
    )
    order_id = cursor.lastrowid

    # save items and reduce stock
    for item in items:
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
            (order_id, item["product_id"], item["qty"], item["price"]),
        )
        cursor.execute(
            "UPDATE products SET stock = stock - ? WHERE product_id = ?",
            (item["qty"], item["product_id"]),
        )

    conn.commit()
    conn.close()

    # clear user cart after success
    clear_cart(username)

    # build simple receipt object
    receipt = {
        "order_id": order_id,
        "username": username,
        "items": items,
        "total": total,
        "discount_code": applied_code,
        "discount_amount": discount_amount,
        "final_total": final_total,
        "timestamp": timestamp,
    }

    return True, "Order placed successfully!", receipt


def get_order_history(username):
    conn = get_connection()
    cursor = conn.cursor()

    # get all orders for this user
    cursor.execute(
        "SELECT order_id, total_price, discount_code, discount_amount, status, created_at FROM orders WHERE username = ? ORDER BY order_id DESC",
        (username,),
    )
    orders = cursor.fetchall()

    order_list = []

    for order in orders:
        # get items for this order
        cursor.execute(
            """
            SELECT oi.product_id, oi.qty, oi.price, p.name
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = ?
        """,
            (order["order_id"],),
        )

        items = []
        for row in cursor.fetchall():
            items.append(
                {
                    "product_id": row["product_id"],
                    "name": row["name"],
                    "qty": row["qty"],
                    "price": row["price"],
                }
            )

        order_list.append(
            {
                "order_id": order["order_id"],
                "total_price": order["total_price"],
                "discount_code": order["discount_code"],
                "discount_amount": order["discount_amount"],
                "status": order["status"],
                "created_at": order["created_at"],
                "items": items,
            }
        )

    conn.close()
    return order_list
