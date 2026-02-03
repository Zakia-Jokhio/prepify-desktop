import sqlite3
import bcrypt
from database_manager import DB_NAME

def handle_login_db(u, p):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password, is_admin, username FROM users WHERE username=?", (u,))
    row = cursor.fetchone()
    conn.close()

    if row:
        stored_hash = row[0]
        # If SQLite returns it as a string, we must encode to bytes for bcrypt
        # If it's already bytes (BLOB), we use it as is
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
            
        if bcrypt.checkpw(p.encode('utf-8'), stored_hash):
            return True, row[1], row[2] 
            
    return False, 0, None

def handle_register_db(u, p):
    # This generates bytes
    hashed = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt())
    try:
        conn = sqlite3.connect(DB_NAME)
        # We store the 'hashed' bytes directly into the database
        conn.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, 0)", (u, hashed))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error: # Better to catch specific DB errors
        return False

def delete_user_from_db(username):
    """Permanently deletes a user and their associated data."""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("DELETE FROM users WHERE username = ?", (username,))
        # Clean up related history so the database stays healthy
        conn.execute("DELETE FROM quiz_history WHERE username = ?", (username,))
        conn.execute("DELETE FROM subject_performance WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Auth DB Error (Delete): {e}")
        return False

def reset_password_in_db(username, new_password):
    """Hashes the new password and updates the database record."""
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("UPDATE users SET password = ? WHERE username = ?", (hashed, username))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Auth DB Error (Reset): {e}")
        return False

def add_admin_db(u, p):
    hashed = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, 1)", (u, hashed))
    conn.commit()
    conn.close()

def add_admin_db(u, p):
    import bcrypt
    hashed = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt())
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, 1)", (u, hashed))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding admin: {e}")
        return False