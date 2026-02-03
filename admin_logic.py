import sqlite3
from database_manager import DB_NAME
import bcrypt

def delete_question(q_id):
    conn = sqlite3.connect(DB_NAME); conn.execute("DELETE FROM questions WHERE rowid = ?", (q_id,)); conn.commit(); conn.close()

def update_question(r_id, data):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""UPDATE questions SET Category=?, Subject=?, Question=?, Option1=?, Option2=?, Option3=?, Option4=?, Answer=? WHERE rowid=?""", (*data, r_id))
    conn.commit(); conn.close()

def add_admin(u, p):
    hashed = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect(DB_NAME); conn.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, 1)", (u, hashed)); conn.commit(); conn.close()