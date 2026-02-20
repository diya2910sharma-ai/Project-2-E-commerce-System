from storage import get_connection


def add_product(name, price, stock):
    # Validate inputs
    if not name or price < 0 or stock < 0:
        return False, "Invalid product data."
    
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            (name, price, stock),
        )
        conn.commit()
        return True, "Product added successfully."
    finally:
        conn.close()


def list_products():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT product_id, name, price, stock FROM products")
    all_rows = c.fetchall()
    conn.close()

    products = []

    for row in all_rows:
        p = {
            "product_id": row["product_id"],
            "name": row["name"],
            "price": row["price"],
            "stock": row["stock"],
        }
        products.append(p)

    return products


def search_products(keyword):
    conn = get_connection()
    cursor = conn.cursor()
    search_word = "%" + keyword.lower() + "%"
    cursor.execute(
        "SELECT product_id, name, price, stock FROM products WHERE LOWER(name) LIKE ?",
        (search_word,),
    )
    rows = cursor.fetchall()
    conn.close()

    products = []

    for row in rows:
        p = {
            "product_id": row["product_id"],
            "name": row["name"],
            "price": row["price"],
            "stock": row["stock"],
        }
        products.append(p)

    return products


def get_product(product_id):
    # find one product by id
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT product_id, name, price, stock FROM products WHERE product_id = ?",
        (product_id,),
    )
    row = c.fetchone()
    conn.close()

    if row:
        p = {
            "product_id": row["product_id"],
            "name": row["name"],
            "price": row["price"],
            "stock": row["stock"],
        }
        return p

    return None
