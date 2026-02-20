from storage import get_connection
import hashlib


def hash_password(password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash


def register(username, password):
    if not username:
        return False, "Username cannot be empty."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if row:
        conn.close()
        return False, "Username already exists."

    password_hash = hash_password(password)

    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )

    conn.commit()
    conn.close()
    return True, "Registration successful!"


def login(username, password):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "SELECT password_hash FROM users WHERE username = ?", (username,)
    )
    row = c.fetchone()

    if not row:
        conn.close()
        return False, "User not found."

    stored_hash = row["password_hash"]
    password_hash = hash_password(password)

    conn.close()

    if password_hash == stored_hash:
        return True, "Login successful!"
    else:
        return False, "Incorrect password."
