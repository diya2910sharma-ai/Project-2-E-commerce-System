from storage import get_connection
import hashlib
import secrets


def hash_password(password, salt):
    # make one string and hash it
    data = salt + password
    return hashlib.sha256(data.encode()).hexdigest()


def register(username, password):
    # check username
    if not username:
        return False, "Username cannot be empty."

    # check password length
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    # connect to db
    conn = get_connection()
    cursor = conn.cursor()

    # see if username already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if row:
        conn.close()
        return False, "Username already exists."

    # generate salt and hash password
    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)

    # insert new user
    cursor.execute(
        "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
        (username, password_hash, salt),
    )

    conn.commit()
    conn.close()
    return True, "Registration successful!"


def login(username, password):
    # connect to db
    conn = get_connection()
    cursor = conn.cursor()

    # find this user
    cursor.execute(
        "SELECT password_hash, salt FROM users WHERE username = ?", (username,)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return False, "User not found."

    # verify password
    stored_hash = row["password_hash"]
    salt = row["salt"]
    password_hash = hash_password(password, salt)

    conn.close()

    if password_hash == stored_hash:
        return True, "Login successful!"
    else:
        return False, "Incorrect password."
