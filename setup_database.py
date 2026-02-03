"""
setup_database.py
-----------------
Initializes a local SQLite database named Prepify.db with Hashed Passwords.
"""
import sqlite3
import bcrypt  
from datetime import datetime

# Connect or create Prepify database
conn = sqlite3.connect('Prepify.db')
c = conn.cursor()

# ---------------------------
# Create tables
# ---------------------------

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT UNIQUE,
    password TEXT,
    is_admin INTEGER DEFAULT 0
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS questions (
    QUESTION TEXT,
    OPTION1 TEXT,
    OPTION2 TEXT,
    OPTION3 TEXT,
    OPTION4 TEXT,
    ANSWER TEXT,
    CATEGORY TEXT,
    SUBJECT TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS quiz_history (
    username TEXT,
    score INTEGER,
    total INTEGER,
    percentage REAL,
    timestamp DATETIME
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS subject_performance (
    username TEXT,
    subject TEXT,
    correct INTEGER,
    total INTEGER,
    timestamp DATETIME
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    subject TEXT,
    score_percent REAL,
    date TEXT,
    category_name TEXT
)
''')

# ---------------------------
# Helper function for Hashing
# ---------------------------
def hash_pw(plain_text_password):
    # Salts and hashes the password, then returns it as a string for SQLite
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# ---------------------------
# Insert users (ADMIN + STUDENTS) with Hashing
# ---------------------------
# We keep the display list for the final print statement
raw_users = [
    ('Admin', 'admin123', 1),
    ('Ali', 'ali123', 0),
    ('Sara', 'sara123', 0),
    ('Ahmed', 'ahmed123', 0)
]

# Processed list with hashed passwords
hashed_users = [(u, hash_pw(p), a) for u, p, a in raw_users]

c.executemany(
    "INSERT OR IGNORE INTO users VALUES (?, ?, ?)",
    hashed_users
)

# ---------------------------
# Insert sample questions data
# ---------------------------
questions = [
    ('Primary site of protein synthesis?', 'Lysosome', 'Ribosome', 'Mitochondria', 'Golgi body', 'Ribosome', 'MDCAT', 'Biology'),
    ('Chemical structure that stores genetic information?', 'RNA', 'DNA', 'ATP', 'Lipids', 'DNA', 'MDCAT', 'Biology'),
    ('Site of aerobic respiration?', 'Cytoplasm', 'Golgi apparatus', 'Mitochondria', 'Ribosome', 'Mitochondria', 'MDCAT', 'Biology'),
    ('Most abundant protein in blood plasma?', 'Hemoglobin', 'Albumin', 'Fibrinogen', 'Myosin', 'Albumin', 'MDCAT', 'Biology'),
    ('pH of pure water at 25°C?', '7', '5', '9', '3', '7', 'MDCAT', 'Chemistry'),
    ('Which bond is most polar?', 'C-H', 'O-H', 'C-C', 'N-N', 'O-H', 'MDCAT', 'Chemistry'),
    ('Newton\'s first law is also known as?', 'Law of gravity', 'Law of inertia', 'Law of motion', 'Hooke\'s law', 'Law of inertia', 'MDCAT', 'Physics'),
    ('Unit of electric current?', 'Volt', 'Ohm', 'Ampere', 'Watt', 'Ampere', 'MDCAT', 'Physics'),
    ('DNA unzipping enzyme?', 'Ligase', 'Primase', 'Helicase', 'Polymerase', 'Helicase', 'MDCAT', 'Biology'),
    ('A plane mirror produces an image that is?', 'Real and inverted', 'Virtual and erect', 'Magnified', 'Smaller', 'Virtual and erect', 'MDCAT', 'Physics'),
    ('Unit of Force?', 'Joule', 'Newton', 'Watt', 'Pascal', 'Newton', 'ECAT', 'Physics'),
    ('Choose the correctly spelled word:', 'Accomodate', 'Acomodate', 'Accommodate', 'Acommadate', 'Accommodate', 'MDCAT', 'English'),
    ('Antibody that crosses placenta?', 'IgA', 'IgM', 'IgG', 'IgE', 'IgG', 'MDCAT', 'Biology'),
    ('Functional group in ethanol?', 'Amino', 'Hydroxyl', 'Carbonyl', 'Sulfhydryl', 'Hydroxyl', 'MDCAT', 'Chemistry'),
    ('Speed of light in vacuum?', '3 x 10^8 m/s', ' 3 x 10^6 m/s', '3 x 10^5 m/s', '3 x 10^7 m/s', '3 x 10^8 m/s', 'MDCAT', 'Physics'),
    ('Covalent bond is formed by?', 'Transfer of electrons', 'Sharing of electrons', 'Ion exchange', 'Magnetic force', 'Sharing of electrons', 'MDCAT', 'Chemistry'),
    ('Ohm\'s law relates?', 'Voltage & current', 'Mass & weight', 'Temperature & pressure', 'Force & distance', 'Voltage & current', 'MDCAT', 'Physics'),
    ('Which gas is most abundant in atmosphere?', 'Oxygen', 'Nitrogen', 'Carbon dioxide', 'Hydrogen', 'Nitrogen', 'MDCAT', 'Chemistry'),
    ('Protein synthesis occurs in?', 'Nucleus', 'Ribosome', 'Lysosome', 'Vacuole', 'Ribosome', 'MDCAT', 'Biology'),
    ('Antonym of ABUNDANT?', 'Plentiful', 'Sparse', 'Ample', 'Bountiful', 'Sparse', 'ECAT', 'English'),
    ('Derivative of x²?', 'x', '2x', 'x²', '1', '2x', 'ECAT', 'Math'),
    ('Synonym of FAST?', 'Quick', 'Slow', 'Late', 'Weak', 'Quick', 'ECAT', 'English'),
    ('Acceleration due to gravity is about?', '9.8 m/s²', '8 m/s²', '10 m/s²', '12 m/s²', '9.8 m/s²', 'ECAT', 'Physics'),
    ('Which solvent is polar?', 'Oil', 'Benzene', 'Water', 'Hexane', 'Water', 'ECAT', 'Chemistry'),
    ('Quadratic formula solves?', 'ax² + bx + c = 0', 'ax + b = 0', 'x³ + 1 = 0', 'ln x = 0', 'ax² + bx + c = 0', 'ECAT', 'Math'),
    ('Vector has both?', 'Magnitude & direction', 'Size only', 'Direction only', 'Color', 'Magnitude & direction', 'ECAT', 'Physics'),
    ('Simplify: 2(x + 3)?', '2x + 3', '2x + 6', 'x + 6', '2x - 3', '2x + 6', 'ECAT', 'Math'),
    ('LCM of 6 and 8?', '12', '24', '18', '48', '24', 'ECAT', 'Math'),
]

c.executemany('''
INSERT OR IGNORE INTO questions
(QUESTION, OPTION1, OPTION2, OPTION3, OPTION4, ANSWER, CATEGORY, SUBJECT)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', questions)

# ---------------------------
# Insert quiz history data 
# ---------------------------
now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
quiz_history = [
    ('Ali', 15, 20, 75.0, now_str),
    ('Sara', 18, 20, 90.0, now_str),
    ('Ahmed', 12, 20, 60.0, now_str)
]

c.executemany(
    "INSERT INTO quiz_history VALUES (?, ?, ?, ?, ?)",
    quiz_history
)

# ---------------------------
# Insert subject performance data
# ---------------------------
performance = [
    ('Ali', 'Biology', 8, 10, now_str),
    ('Sara', 'Math', 9, 10, now_str),
    ('Ahmed', 'English', 6, 10, now_str)
]

c.executemany(
    "INSERT INTO subject_performance VALUES (?, ?, ?, ?, ?)",
    performance
)

# ---------------------------
# Insert sample quiz_results data
# ---------------------------
quiz_results = [
    ( 'Ali', 'Biology', 75.0, now_str, 'MDCAT'),
    ( 'Sara', 'Math', 90.0, now_str, 'ECAT'),
    ( 'Ahmed', 'English', 60.0, now_str, 'ECAT')
]

c.executemany('''
INSERT INTO quiz_results (user_id, subject, score_percent, date, category_name)
VALUES (?, ?, ?, ?, ?)
''', quiz_results)

# Commit & close
conn.commit()
conn.close()

# ---------------------------
# Print login details
# ---------------------------
print("\n Prepify Database Setup Complete with Secure Hashing!\n")
print(" TEST LOGIN CREDENTIALS:\n")

for u, p, a in raw_users:
    role = "ADMIN" if a == 1 else "USER"
    print(f"{role} → Username: {u} | Password: {p}")

print("\n You can now run main.py")