from storage import get_connection
from products import get_product


def add_to_cart(username, product_id, qty):
    if qty <= 0:
        return False, "Quantity should be greater than zero."

    product = get_product(product_id)
    if not product:
        return False, "Product unavailable."

    if qty > product["stock"]:
        return False, "Not enough stock."

    conn = get_connection()
    try:
        c = conn.cursor()

        c.execute(
            "SELECT qty FROM carts WHERE username = ? AND product_id = ?",
            (username, product_id),
        )
        row = c.fetchone()

        if row:
            new_qty = row["qty"] + qty
            if new_qty > product["stock"]:
                return False, "Total quantity exceeds available stock."
            c.execute(
                "UPDATE carts SET qty = ? WHERE username = ? AND product_id = ?",
                (new_qty, username, product_id),
            )
        else:
            c.execute(
                "INSERT INTO carts (username, product_id, qty) VALUES (?, ?, ?)",
                (username, product_id, qty),
            )

        conn.commit()
        return True, "Added to cart!"
    finally:
        conn.close()


def remove_from_cart(username, product_id, qty=None):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "SELECT qty FROM carts WHERE username = ? AND product_id = ?",
        (username, product_id),
    )
    row = c.fetchone()

    if not row:
        conn.close()
        return False, "Item not in cart."

    current_qty = row["qty"]

    if qty is None or qty >= current_qty:
        # remove entire item
        c.execute(
            "DELETE FROM carts WHERE username = ? AND product_id = ?",
            (username, product_id),
        )
    else:
        # reduce quantity
        new_qty = current_qty - qty
        c.execute(
            "UPDATE carts SET qty = ? WHERE username = ? AND product_id = ?",
            (new_qty, username, product_id),
        )

    conn.commit()
    conn.close()
    return True, "Cart updated."


def get_cart(username):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "SELECT c.product_id, c.qty, p.name, p.price FROM carts c JOIN products p ON c.product_id = p.product_id WHERE c.username = ?",
        (username,),
    )

    rows = c.fetchall()
    conn.close()

    items = []
    total = 0

    for row in rows:
        price = row["price"]
        qty = row["qty"]
        subtotal = qty * price
        total = total + subtotal

        item = {
            "product_id": row["product_id"],
            "name": row["name"],
            "qty": qty,
            "price": price,
            "subtotal": subtotal,
        }
        items.append(item)

    return items, total


def clear_cart(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM carts WHERE username = ?", (username,))
    conn.commit()
    conn.close()
