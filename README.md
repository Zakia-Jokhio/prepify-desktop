#  Prepify — Entry Test Past Paper Quiz Application

**Prepify** is a Python-based desktop quiz application built to help students prepare for competitive entry tests such as **MDCAT, ECAT, and university admission exams**.  
It offers a **modern GUI**, **multiple quiz modes**, **secure role-based access**, **performance analytics**, and **automated reporting** — all in a lightweight offline app.

> 🎯 Built *by a student, for students* — focused on real exam-prep pain points.

---

## 📌 Why Prepify?

Students often struggle with:
- Scattered and unorganized past papers
- No clear way to track performance
- Lack of meaningful feedback after practice

**Prepify centralizes practice, analytics, and reporting** into a single interactive system designed for focused preparation.

---

## ✨ Key Features

### 🧠 Smart Quiz System
- Filter questions by **entry test type** (MDCAT / ECAT) and **subject**
- Dynamic question selection using `pandas`

---

### ⏱️ Quiz Modes
- **Standard Mode** — 60 seconds per question (exam-like practice)
- **Sudden Death Mode** — quiz ends on first wrong answer
- **Speed Sprint Mode** — 10 seconds per question for rapid recall

Each mode uses custom timer logic and controlled quiz flow.

---

### 🛠️ Admin Panel
Admin access is protected via **role checks at login**.

**Question Management**
- Add, edit, and delete questions
- Manage subjects and categories

**User Management**
- View and delete users
- Reset or update passwords
- Add new admin accounts  
*(Admin-managed resets replace a traditional “forgot password” feature)*

---

### 🛡️ Input Validation
- Empty-field checks
- Safe database operations
- Graceful error handling to prevent crashes

---

### 📊 Dashboard (Quick Stats & Recent Activity)
- **Quick Stats:** total quizzes, average score, performance category
- **Recent Activity:** latest quiz attempts with date, category, and score

Designed for **instant progress tracking at a glance**.

---

### 📈 Performance Analytics
- **Weakest Subject Detection** based on past quiz data
- **Trend Graphs** to visualize performance across recent attempts

---

### 📄 Automated PDF Reports
- Generated using **ReportLab**
- Includes:
  - Correct & incorrect answers (color-coded)
  - Quiz mode, score, time taken
  - Date & timestamp (via `datetime`)
- Reports are automatically saved to the user’s **Downloads** folder

---

### 🔐 Secure Authentication
- Passwords are **hashed** (never stored in plain text)
- Persistent and secure storage using **SQLite**

---

## 🛠️ Tech Stack
- **Language:** Python 3.x  
- **Database:** SQLite  
- **GUI:** CustomTkinter  
- **Data Processing:** Pandas  
- **Visualization:** Matplotlib  
- **PDF Generation:** ReportLab  

---

## 📂 Project Structure
Prepify/
│
├── main.py # Application entry point
├── setup_database.py # Database initialization & sample data
├── auth_manager.py # Authentication & role checks
├── database_manager.py # Centralized database operations (CRUD)
├── admin_logic.py # Admin panel & analytics logic
├── report_generator.py # PDF report generation
├── ui_components/ # UI assets
└── README.md # Project documentation


---

## 🧪 Use Cases
- Entry test exam simulation (MDCAT, ECAT, others)
- Identifying weak subjects using analytics
- Improving speed and accuracy with timed modes
- Tracking progress across multiple attempts
- Portfolio-ready desktop application for recruiters

---

## 📈 Planned Enhancements
- Adaptive difficulty based on performance
- Enhanced role-based access control
- Leaderboards and extended progress history
- Export analytics to Excel/PDF
- Optional cloud backup

---

## ⚙️ Installation & Setup

### Clone the Repository
```bash
git clone https://github.com/Zakia-Jokhio/prepify-desktop
cd prepify
pip install pandas matplotlib reportlab customtkinter bcrypt
python main.py

