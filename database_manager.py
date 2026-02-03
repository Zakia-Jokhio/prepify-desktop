import datetime
import sqlite3
from unittest import case
import pandas as pd
from tkinter import messagebox
import bcrypt

DB_NAME = "prepify.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_conn()
    # Ensure all tables exist
    conn.execute("""CREATE TABLE IF NOT EXISTS quiz_history (
                    username TEXT, score INTEGER, total INTEGER, 
                    percentage REAL, timestamp DATETIME)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS subject_performance (
                    username TEXT, subject TEXT, correct INTEGER, 
                    total INTEGER, timestamp DATETIME)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS questions (
                    Category TEXT, Subject TEXT, Question TEXT, 
                    Option1 TEXT, Option2 TEXT, Option3 TEXT, 
                    Option4 TEXT, Answer TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS quiz_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    subject TEXT,
                    score_percent REAL,
                    date TEXT)""")
    conn.commit()
    conn.close()

def get_questions():
    try:
        conn = get_conn()
        df = pd.read_sql_query("SELECT * FROM questions", conn).fillna("N/A")
        # Ensure column names are capitalized to match dataframe logic
        df.columns = [c.capitalize() for c in df.columns]
        conn.close()
        return df
    except Exception as e:
        print(f"Database Error: {e}")
        return pd.DataFrame()


def get_progress_data(username):
    try:
        conn = get_conn()
        query = """
            SELECT SCORE_PERCENT as percentage, DATE as timestamp 
            FROM quiz_results 
            WHERE LOWER(USER_ID) = LOWER(?)
            ORDER BY DATE DESC LIMIT 10
        """
        df = pd.read_sql_query(query, conn, params=(username,))
        conn.close()
        return df
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()
    
def get_weakest_subject_data(username):
    try:
        conn = get_conn()
        # We try to find the subject performance data
        # First, we check if the table exists and use the most likely column names
        try:
            query = """
                SELECT subject, (SUM(correct) * 100.0 / SUM(total)) as avg_acc 
                FROM subject_performance 
                WHERE LOWER(username) = LOWER(?) 
                GROUP BY subject 
                ORDER BY avg_acc ASC 
                LIMIT 1
            """
            weak_data = conn.execute(query, (username,)).fetchone()
        except:
            # Fallback if your table uses 'user' instead of 'username'
            query = """
                SELECT subject, (SUM(correct) * 100.0 / SUM(total)) as avg_acc 
                FROM subject_performance 
                WHERE LOWER(user) = LOWER(?) 
                GROUP BY subject 
                ORDER BY avg_acc ASC 
                LIMIT 1
            """
            weak_data = conn.execute(query, (username,)).fetchone()
            
        conn.close() 
        # This will now show the actual data in your terminal
        print(f"DEBUG: Database found for {username}: {weak_data}")
        return weak_data 
    except Exception as e:
        print(f"Database Error: {e}")
        return None
    

def add_new_question(category, subject, question, o1, o2, o3, o4, answer):
    """Inserts a new question into the database."""
    try:
        conn = get_conn()
        conn.execute("""INSERT INTO questions 
                        (Category, Subject, Question, Option1, Option2, Option3, Option4, Answer) 
                        VALUES (?,?,?,?,?,?,?,?)""", 
                     (category, subject, question, o1, o2, o3, o4, answer))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding question: {e}")
        return False
    
def delete_question_by_id(q_id):
    """Permanently removes a question from the database using its rowid."""
    try:
        conn = get_conn()
        conn.execute("DELETE FROM questions WHERE rowid = ?", (q_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting question: {e}")
        return False
    
def get_all_questions_with_ids():
    """Fetches every question including the rowid for management purposes."""
    try:
        conn = get_conn()
        rows = conn.execute("SELECT rowid, * FROM questions").fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error fetching questions list: {e}")
        return []
    
def get_users_list(current_user, search_query=""):
    """Fetches users from the database, excluding the current logged-in user, with optional search."""
    try:
        conn = get_conn()
        query = "SELECT username, is_admin FROM users WHERE username != ?"
        params = [current_user]
        
        if search_query:
            query += " AND username LIKE ?"
            params.append(f"%{search_query}%")
            
        cursor = conn.execute(query, params)
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []
    
def delete_user_from_db(username):
    """Deletes a user account from the database."""
    try:
        conn = get_conn()
        conn.execute("DELETE FROM users WHERE username = ?", (username,))
        # Also clean up their history to save space
        conn.execute("DELETE FROM quiz_history WHERE username = ?", (username,))
        conn.execute("DELETE FROM subject_performance WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False
    
def get_recent_activity(username):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUBJECT, SCORE_PERCENT, DATE 
            FROM quiz_results 
            WHERE USER_ID = ? 
            ORDER BY DATE DESC 
            LIMIT 5
        """, (username,))
        data = cursor.fetchall()
        conn.close()
        return data
    except Exception as e:
        print(f"DB Error: {e}")
        return []

def reset_password_in_db(username, new_password):
    """Hashes a new password and updates the user's record."""
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    try:
        conn = get_conn()
        conn.execute("UPDATE users SET password = ? WHERE username = ?", (hashed, username))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error resetting password: {e}")
        return False
    
def get_managed_questions(search_query=""):
    """Fetches questions with their rowid, supporting the live search filter."""
    try:
        conn = get_conn()
        if search_query:
            # Search across Question text or Subject
            query = "SELECT rowid, * FROM questions WHERE Question LIKE ? OR Subject LIKE ?"
            cursor = conn.execute(query, (f"%{search_query}%", f"%{search_query}%"))
        else:
            query = "SELECT rowid, * FROM questions"
            cursor = conn.execute(query)
            
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Database Error (Search): {e}")
        return []

def update_question(q_id, category, subject, question, o1, o2, o3, o4, answer):
    """Updates an existing question in the database using its rowid."""
    try:
        conn = get_conn()
        conn.execute("""UPDATE questions SET 
                        Category=?, Subject=?, Question=?, 
                        Option1=?, Option2=?, Option3=?, Option4=?, Answer=? 
                        WHERE rowid=?""", 
                     (category, subject, question, o1, o2, o3, o4, answer, q_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database Error (Update): {e}")
        return False
    
def get_user_dashboard_data(username):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        # 1. Use LOWER to ensure we match correctly
        cursor.execute("""
            SELECT COUNT(*), AVG(SCORE_PERCENT) 
            FROM quiz_results 
            WHERE LOWER(USER_ID) = LOWER(?)
        """, (username,))
        stats = cursor.fetchone()
        
        cursor.execute("""
            SELECT DATE, category_name, SCORE_PERCENT 
            FROM quiz_results 
            WHERE LOWER(USER_ID) = LOWER(?) 
            ORDER BY ID DESC LIMIT 5
        """, (username,))
        history = cursor.fetchall()
        conn.close()
        # Debugging: Check the terminal to see what the DB actually found
        print(f"DEBUG: Found {stats[0]} quizzes for user: {username}")
        return {
            'total_quizzes': stats[0] if stats else 0,
            'avg_score': round(stats[1], 1) if stats and stats[1] else 0,
            'recent_activity': history
        }
    except Exception as e:
        print(f"Database Error: {e}")
        return {'total_quizzes': 0, 'avg_score': 0, 'recent_activity': []}

    
def save_quiz_results(self, user, score, total, percentage, category, timestamp, quiz_data, answers):
    conn = get_conn()
    # 1. Insert into quiz_results table
    main_subject = quiz_data['Subject'].iloc[0] if hasattr(quiz_data, 'iloc') else "General"
    conn.execute("""
        INSERT INTO quiz_results (USER_ID, SUBJECT, category_name, SCORE_PERCENT, DATE)
        VALUES (?, ?, ?, ?, ?)
    """, (user, main_subject, category, percentage, timestamp))
    # 2. Keep your Subject Performance logic (This works for the Weakest Subject feature)
    if hasattr(quiz_data, 'groupby'): 
        for subj in quiz_data['Subject'].unique():
            s_df = quiz_data[quiz_data['Subject'] == subj]
            s_cor = sum(1 for i, q in s_df.iterrows() if str(answers.get(i)) == str(q["Answer"]))
            s_perc = (s_cor / len(s_df)) * 100
            
            conn.execute("""
                INSERT INTO subject_performance (USERNAME, SUBJECT, CORRECT, TOTAL, TIMESTAMP) 
                VALUES (?, ?, ?, ?, ?)
            """, (user, subj, s_cor, len(s_df), timestamp))
    conn.commit()
    conn.close()

def update_subject_performance(username, subject, correct, total):
    conn = get_conn()
    # Check if subject already exists for this user
    query = "SELECT 1 FROM subject_performance WHERE username=? AND subject=?"
    exists = conn.execute(query, (username, subject)).fetchone()
    if exists:
        conn.execute("""
            UPDATE subject_performance 
            SET correct = correct + ?, total = total + ? 
            WHERE username=? AND subject=?
        """, (correct, total, username, subject))
    else:
        conn.execute("""
            INSERT INTO subject_performance (username, subject, correct, total) 
            VALUES (?, ?, ?, ?)
        """, (username, subject, correct, total))
    conn.commit()
    conn.close()


