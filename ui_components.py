import customtkinter as ctk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import sqlite3
from database_manager import *

class WelcomeFrame(ctk.CTkFrame):
    def __init__(self, master, auth_callback, **kwargs):
        super().__init__(master, corner_radius=20, **kwargs)
        # Title
        ctk.CTkLabel(self, text="PREPIFY", font=("Segoe UI", 38, "bold"), 
                     text_color="#3B8ED0").pack(pady=(50, 10), padx=40)
        # Subtitle
        ctk.CTkLabel(self, text="Your path to excellence starts here.", 
                     font=("Segoe UI", 16)).pack(pady=(0, 40), padx=20)
        # Login Button
        ctk.CTkButton(self, text="LOGIN", font=("Segoe UI", 16, "bold"), width=300, height=50, 
                      command=lambda: auth_callback("login")).pack(pady=10, padx=40)
        # Register Button
        ctk.CTkButton(self, text="CREATE ACCOUNT", font=("Segoe UI", 16), width=300, height=50, 
                      fg_color="transparent", border_width=2, text_color=("#3B8ED0", "white"), 
                      command=lambda: auth_callback("register")).pack(pady=10, padx=40)
        

class AuthFrame(ctk.CTkFrame):
    def __init__(self, master, mode, login_cmd, register_cmd, back_cmd, win_width, **kwargs):
        # We put the main content inside a frame which sits inside the scrollable master
        super().__init__(master, corner_radius=20, **kwargs)
        title_text = "WELCOME BACK" if mode == "login" else "JOIN PREPIFY"
        ctk.CTkLabel(self, text=title_text, font=("Segoe UI", 32, "bold"), 
                     text_color="#3B8ED0").pack(pady=(40, 30), padx=20)
        # Responsive width logic
        field_width = 320 if win_width > 600 else 260
        # Create entries as attributes of THIS class so they are accessible
        self.auth_user = ctk.CTkEntry(self, placeholder_text="Username", width=field_width, height=45)
        self.auth_user.pack(pady=12, padx=20)
        self.auth_pass = ctk.CTkEntry(self, placeholder_text="Password", width=field_width, height=45, show="*")
        self.auth_pass.pack(pady=12, padx=20)
        # Determine command based on mode
        cmd = login_cmd if mode == "login" else register_cmd
        ctk.CTkButton(self, text="PROCEED", font=("Segoe UI", 16, "bold"), 
                      width=field_width, height=50, command=cmd).pack(pady=(30, 10))
        
        if mode == "login":
            ctk.CTkLabel(self, text="Forgot password? Contact Admin", font=("Arial", 11, "italic"), 
                         text_color="gray", wraplength=250).pack(pady=5)
            
        ctk.CTkButton(self, text="⬅ Go Back", fg_color="transparent", 
                      text_color="gray", command=back_cmd).pack(pady=5)
    

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, is_admin, categories, subjects_df, commands, subjects, user_name="User", **kwargs):
        self.win_width = kwargs.pop('win_width', None)
        # Extract the real database stats passed from main.py
        self.stats_data = kwargs.pop('stats_data', {'total_quizzes': 0, 'avg_score': 0, 'best_subject': 'N/A', 'recent_activity': []})
        super().__init__(master, fg_color="transparent", **kwargs)
        # This is your database (self.full_df from main.py)
        self.is_admin = is_admin
        self.full_df = subjects_df 
        self.subjects_list = subjects 
        self.commands = commands
        self.user_name = user_name

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=35, fg_color=("#EBF5FF", "#333333")) 
        self.sidebar.pack(side="left", fill="y", padx=20, pady=20)
        self.sidebar.pack_propagate(False)
        ctk.CTkLabel(self.sidebar, text="PREPIFY", font=("Segoe UI", 28, "bold"), 
                     text_color=("#007AFF", "#3B8ED0")).pack(pady=(40, 20))
        
        if is_admin == 1:
            ctk.CTkButton(self.sidebar, text="ADMIN PANEL ⚙", fg_color="#FF9800", hover_color="#E68A00", 
                          text_color="white", font=("Segoe UI", 13, "bold"), height=45, corner_radius=25,
                          command=commands['admin']).pack(pady=10, padx=20, fill="x")
        btn_bg, btn_hover, btn_text = ("#D1E9FF", "#4D4D4D"), ("#A5D1FF", "#666666"), ("#005FB8", "white")
        
        for txt, cmd in [("Light Mode", lambda: ctk.set_appearance_mode("light")), 
                         ("Dark Mode", lambda: ctk.set_appearance_mode("dark")),
                         ("PROGRESS", commands['progress']), ("WEAK SUBJECTS", commands['weak'])]:
            ctk.CTkButton(self.sidebar, text=txt, height=40, corner_radius=20, fg_color=btn_bg, 
                          hover_color=btn_hover, text_color=btn_text, command=cmd).pack(pady=5, padx=20, fill="x")
        
        ctk.CTkButton(self.sidebar, text="LOGOUT", height=45, corner_radius=20, fg_color="#D32F2F", 
                      hover_color="#B71C1C", font=("Segoe UI", 13, "bold"), text_color="white", 
                      command=commands['logout']).pack(side="bottom", pady=30, padx=20, fill="x")

        # --- MAIN CONTENT ---
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(side="right", expand=True, fill="both", padx=20, pady=20)
        
        welcome_section = ctk.CTkFrame(main_content, fg_color=("#EBF5FF", "#333333"), corner_radius=25)
        welcome_section.pack(fill="x", pady=(0, 10))

        # --- WELCOME MESSAGE HEADING ---
        ctk.CTkLabel(welcome_section, text=f"Welcome back, {self.user_name}!", 
                     font=("Segoe UI", 28, "bold"), text_color=("#007AFF", "#3B8ED0"), justify="left").pack(anchor="w", padx=35, pady=(25, 0))
        
        # --- SUB-HEADING ---
        ctk.CTkLabel(welcome_section, text="Ready to ace your test? Let's get started.", 
                    font=("Segoe UI", 15, "normal"), text_color=("#005FB8", "#A0A0A0"), justify="left").pack(anchor="w", padx=37, pady=(5, 25))

        # --- BOTTOM AREA ---
        bottom_area = ctk.CTkFrame(main_content, fg_color="transparent")
        bottom_area.pack(fill="both", expand=True)

        # --- CONFIGURATION CARD ---
        self.config_card = ctk.CTkFrame(bottom_area, fg_color=("#EBF5FF", "#2B2B2B"), corner_radius=25, width=380)
        self.config_card.pack(side="left", fill="y", padx=(0, 15))
        self.config_card.pack_propagate(False)
        ctk.CTkLabel(self.config_card, text="Configuration", font=("Segoe UI", 20, "bold")).pack(pady=(10, 5))
           # 1. Category Selection
        self.cat_cb = ctk.CTkOptionMenu(self.config_card, values=categories, width=300, height=35, corner_radius=10, 
                                        command=self.update_subjects)
        self.cat_cb.set("Select Category")
        # Update the command to tell the App when you change it
        command=lambda choice: (self.update_subjects(choice), getattr(self.master, 'update_app_category', 
            getattr(self.master, 'update_app_category', lambda x: None))(choice)
            )
        self.cat_cb.configure(command=command)
        self.cat_cb.pack(pady=5)
            # 2. Subject Selection
        ctk.CTkLabel(self.config_card, text="SELECT SUBJECTS", font=("Segoe UI", 11, "bold")).pack(pady=2)
        self.sub_frame = ctk.CTkFrame(self.config_card, fg_color="transparent")
        self.sub_frame.pack(pady=2, fill="x")
        self.update_subjects("Select Category")
            # 3. Question Count
        self.num_ent = ctk.CTkEntry(self.config_card, placeholder_text="Question Count", width=300, height=35)
        self.num_ent.pack(pady=5)
            # 4. Quiz Mode
        ctk.CTkLabel(self.config_card, text="SELECT QUIZ MODE", font=("Segoe UI", 11, "bold")).pack(pady=2)
        self.mode_var = ctk.StringVar(value="Standard")
        self.mode_desc_var = ctk.StringVar(value="Standard: 60s per question.")
        mode_f = ctk.CTkFrame(self.config_card, fg_color="transparent")
        mode_f.pack(pady=2)
        for m_text, m_val in [("Standard", "Standard"), ("Sudden Death", "Death"), ("Speed Sprint", "Sprint")]:
            ctk.CTkRadioButton(mode_f, text=m_text, variable=self.mode_var, value=m_val, 
                               command=self.update_mode_description,
                               font=("Segoe UI", 10), radiobutton_width=18, radiobutton_height=18).pack(side="left", padx=5)
        ctk.CTkLabel(self.config_card, textvariable=self.mode_desc_var, font=("Segoe UI", 10, "italic"), text_color="gray").pack(pady=2)
            # 5. Start Quiz Button
        self.start_btn = ctk.CTkButton(self.config_card, text="START QUIZ", font=("Segoe UI", 16, "bold"), 
                                      width=300, height=42, corner_radius=15, command=commands['start'])
        self.start_btn.pack(side="bottom", pady=20)

        # --- RIGHT PANEL ---
        right_panel = ctk.CTkFrame(bottom_area, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True)

            # 1. Quick Stats Card
        stats_card = ctk.CTkFrame(right_panel, fg_color=("#EBF5FF", "#333333"), corner_radius=25)
        stats_card.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(stats_card, text="Quick Stats", font=("Segoe UI", 18, "bold"), text_color=("#007AFF", "#3B8ED0")).pack(pady=10)
        # Stats Row - Using real data keys
        stats_f = ctk.CTkFrame(stats_card, fg_color="transparent")
        stats_f.pack(fill="x", padx=20, pady=10)
        # Mapping stats from your database dictionary
        real_stats = [
            ("Quizzes", str(self.stats_data['total_quizzes']), "#4CAF50"),
            ("Avg Score", f"{self.stats_data['avg_score']}%", "#007AFF"),
            ("Category", "Overall", "#FF9800")
        ]
        # Determine color: use provided 'col' unless it's the Avg Score
        for label, val, col in real_stats:
            display_col = col
            if label == "Avg Score":
                clean_val = val.replace('%', '')
                display_col = self.get_score_color(clean_val)
        # for label, val, col in real_stats:
            f = ctk.CTkFrame(stats_f, fg_color="transparent")
            f.pack(side="left", expand=True)
            ctk.CTkLabel(f, text=val, font=("Segoe UI", 20, "bold"), text_color=display_col).pack()
            ctk.CTkLabel(f, text=label, font=("Segoe UI", 10)).pack()

           # 2. Recent Activity Card
        activity_card = ctk.CTkFrame(right_panel, fg_color=("#EBF5FF", "#333333"), corner_radius=25)
        activity_card.pack(fill="both", expand=True)
        ctk.CTkLabel(activity_card, text="Recent Activity", font=("Segoe UI", 18, "bold"), text_color=("#007AFF", "#3B8ED0")).pack(pady=10)
        # Using real activity list from database
        user_activities = self.stats_data['recent_activity']
        if not user_activities:
            ctk.CTkLabel(activity_card, text="No quizzes taken yet!", font=("Segoe UI", 12, "italic")).pack(pady=20)
        else:
            for row in user_activities:
                current_cat = row[0]
                current_score = row[1]
                current_date = row[2]
                item = ctk.CTkFrame(activity_card, fg_color="transparent")
                item.pack(fill="x", padx=20, pady=5)
                # Logic to find which part of the row is the score and which is the date
                current_score = 0.0
                current_date = "Recent"
                current_cat = "Quiz"
                
                for val in row:
                    val_str = str(val)
                    if '-' in val_str and ':' in val_str: # It's the date/timestamp
                        try:
                            date_obj = datetime.strptime(val_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                            current_date = date_obj.strftime('%d %b')
                        except: current_date = val_str[:10]
                    elif isinstance(val, (int, float)) or (val_str.replace('.','',1).isdigit()): # It's the score
                        current_score = float(val)
                    else: # It's the Category/Subject
                        current_cat = val_str

                #  Dynamic Label for date and category like: "31 Jan - MDCAT"
                display_text = f"{current_date} - {current_cat}"
                ctk.CTkLabel(item, text=display_text, font=("Segoe UI", 12)).pack(side="left")
                
                # Safe Rounded Score
                ctk.CTkLabel(item, text=f"{current_score:.1f}%", font=("Segoe UI", 12, "bold"), text_color="#4CAF50").pack(side="right")
                ctk.CTkFrame(activity_card, height=1, fg_color=("#D1E9FF", "#4D4D4D")).pack(fill="x", padx=30, pady=2)

        # Clear History Button Logic
        self.clear_history_btn = ctk.CTkButton(
            activity_card, 
            text="CLEAR ALL HISTORY",
            fg_color="#E74C3C", 
            hover_color="#C0392B",
            font=("Segoe UI", 12, "bold"),
            height=40,
            corner_radius=20,
            command=self.confirm_clear_history
        )
        self.clear_history_btn.pack(pady=20, padx=20)

    def update_mode_description(self):
        modes = {
            "Standard": "Standard: 60s per question.",
            "Death": "Sudden Death: One wrong answer and it's over!",
            "Sprint": "Speed Sprint: 10 seconds per question!"
        }
        self.mode_desc_var.set(modes.get(self.mode_var.get()))

    def toggle_all_subjects(self):
        state = self.all_var.get()
        for var in self.subject_vars.values():
            var.set(state)

    def confirm_clear_history(self):
        if messagebox.askyesno("Confirm Delete", "This will permanently erase all your quiz records. Continue?"):
            self.perform_deletion()

    def get_score_color(self, score):
        """Returns a color hex code based on the score percentage."""
        try:
            score_val = float(score)
            if score_val >= 80:
                return "#2ecc71"  # Green
            elif score_val >= 50:
                return "#f1c40f"  # Yellow/Gold
            else:
                return "#e74c3c"  # Red
        except (ValueError, TypeError):
            return "#ffffff"  # Default White if score is N/A

    def perform_deletion(self):
        try:
            with sqlite3.connect('prepify.db') as conn:
                cursor = conn.cursor()
                # 1. Clear Quiz Stats & History
                cursor.execute("DELETE FROM quiz_results WHERE user_id = ?", (self.user_name,))
                try:
                    cursor.execute("DELETE FROM quiz_history WHERE user = ?", (self.user_name,))
                except sqlite3.OperationalError:
                    cursor.execute("DELETE FROM quiz_history WHERE username = ?", (self.user_name,))
                # 2. Clear performance table
                cursor.execute("DELETE FROM subject_performance WHERE username = ?", (self.user_name,))
                conn.commit()
                # 3. Refresh the UI
            if 'dash_cmd' in self.commands:
                self.commands['dash_cmd'](self.is_admin, self.user_name)
                messagebox.showinfo("Success", "All history and performance data cleared!")
        except Exception as e:
                messagebox.showinfo("Error", f"Failed to refresh UI: {e}")
            

    def update_subjects(self, selected_category):
        for widget in self.sub_frame.winfo_children():
            widget.destroy()
        self.subject_vars = {}
        if selected_category == "Select Category":
            ctk.CTkLabel(self.sub_frame, text="Select a category to load subjects", font=("Segoe UI", 11, "italic")).pack(pady=10)
            return
        
        filtered_subjects = self.full_df[self.full_df['Category'] == selected_category]['Subject'].unique().tolist()
        for s in filtered_subjects:
            var = ctk.BooleanVar()
            self.subject_vars[s] = var
            ctk.CTkCheckBox(self.sub_frame, text=s, variable=var, font=("Segoe UI", 12), 
                            checkbox_width=18, checkbox_height=18, corner_radius=50).pack(pady=1, anchor="w", padx=60)
        
        self.all_var = ctk.BooleanVar()
        ctk.CTkCheckBox(self.sub_frame, text="All", variable=self.all_var, checkbox_width=18, 
                        checkbox_height=18, corner_radius=50, command=self.toggle_all_subjects, 
                        font=("Segoe UI", 12, "bold")).pack(pady=2, anchor="w", padx=60)
             

class QuizFrame(ctk.CTkFrame):
    def __init__(self, master, current_q, total_q, question_data, saved_answer, next_cmd, prev_cmd, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        # 1. Centered Red Timer Label
        self.timer_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 24, "bold"), text_color="#E91E63")
        self.timer_label.pack(pady=(20, 10))
        
        # 2. Main Question Card
        self.card = ctk.CTkFrame(self, corner_radius=20)
        self.card.pack(expand=True, fill="both", padx=40, pady=20)
        
        # 3. Question Counter
        counter_text = f"Question {current_q + 1} of {total_q}"
        ctk.CTkLabel(self.card, text=counter_text, font=("Segoe UI", 16)).pack(pady=(20, 0))
        
        # 4. Question Text
        self.question_label = ctk.CTkLabel(self.card, text=question_data['Question'], 
                                           font=("Segoe UI", 26, "bold"), wraplength=900)
        self.question_label.pack(pady=30)
        
        # 5. Radio Buttons for Options
        self.opt_var = ctk.StringVar(value=saved_answer)
        for i in range(1, 5):
            ctk.CTkRadioButton(self.card, text=str(question_data[f'Option{i}']), 
                               value=str(question_data[f'Option{i}']), 
                               variable=self.opt_var,
                               font=("Segoe UI", 14),
                               border_width_checked=6).pack(pady=10, anchor="w", padx=100)
        
        # 6. Navigation Footer
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", side="bottom", pady=30)
        btn_next_text = "Finish" if current_q == total_q - 1 else "Next ➡"
        ctk.CTkButton(footer, text=btn_next_text, width=150, height=40, font=("Segoe UI", 14, "bold"),
                      command=next_cmd).pack(side="right", padx=60)
        
        if current_q > 0: 
            ctk.CTkButton(footer, text="⬅ Back", width=150, height=40, font=("Segoe UI", 14, "bold"),
                          command=prev_cmd).pack(side="left", padx=60)
            

class ResultsFrame(ctk.CTkFrame):
    def __init__(self, master, last_score, last_total, report_module, review_cmd, dash_cmd, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        # 1. Green Header Label
        ctk.CTkLabel(self, text="QUIZ COMPLETE", 
                     font=("Segoe UI", 38, "bold"), 
                     text_color="#4CAF50").pack(pady=(30, 10))
        
        # 2. Main Card Frame with Pie Chart
        card_color = ("#ebebeb", "#2b2b2b") 
        card = ctk.CTkFrame(self, corner_radius=20, fg_color=card_color)
        card.pack(pady=10, padx=40, fill="both", expand=True)
        
        # 3. Final Score Label 
        score_text = f"Final Score: {last_score} / {last_total}"
        ctk.CTkLabel(card, text=score_text, 
                     font=("Segoe UI", 28)).pack(pady=(20, 0))

        # 4. Pie Chart Container
        chart_container = ctk.CTkFrame(card, fg_color=card_color) 
        chart_container.pack(expand=True, fill="both", pady=0)

        # Call the generator from the report module
        chart = report_module.generate_pie_chart(chart_container, last_score, last_total, ctk.get_appearance_mode())
        
        chart_widget = chart.get_tk_widget()
        chart_widget.pack(expand=True, fill="both")
        chart.draw()
        
        # 5. Bottom Navigation Buttons 
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="Detailed Review", 
                       width=220, height=45, font=("Segoe UI", 14, "bold"),
                       command=review_cmd).pack(pady=5)
        
        ctk.CTkButton(btn_frame, text="Go to Dashboard", 
                       width=220, height=45, font=("Segoe UI", 14, "bold"),
                       command=dash_cmd, fg_color="gray", hover_color="#555555").pack(pady=5)
        

class ReviewFrame(ctk.CTkFrame):
    def __init__(self, master, quiz_data, answers, back_cmd, save_cmd, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        # Header with Save PDF and Back buttons
        header = ctk.CTkFrame(self, height=70, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(header, text="⬅ Back", width=100, command=back_cmd).pack(side="left", padx=10)
        ctk.CTkButton(header, text="💾 SAVE AS PDF", fg_color="#28a745", command=save_cmd).pack(side="right", padx=10)
        
        # Main Scrollable Area
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=40, pady=10)
        
        for i, q in quiz_data.iterrows():
            # Question Container
            f = ctk.CTkFrame(scroll, fg_color="transparent")
            f.pack(fill="x", pady=5)
            
            u_ans = answers.get(i, "None")
            cor_ans = str(q['Answer'])
            is_correct = str(u_ans) == cor_ans
            
            # Question Text
            ctk.CTkLabel(f, text=f"Q{i+1}: {q['Question']}", 
                         font=("Segoe UI", 15, "bold"), 
                         wraplength=900, anchor="w", justify="left").pack(fill="x", padx=10)
            
            # Status text
            status_text = "[CORRECT]" if is_correct else "[INCORRECT]"
            ctk.CTkLabel(f, text=f"Your Answer: {u_ans} {status_text}", 
                         text_color="#4CAF50" if is_correct else "#E91E63", 
                         font=("Segoe UI", 13)).pack(anchor="w", padx=30)
            
            # Show Correct Answer only if user was wrong
            if not is_correct:
                ctk.CTkLabel(f, text=f"Correct Answer: {cor_ans}", 
                             text_color="#4CAF50", 
                             font=("Segoe UI", 13)).pack(anchor="w", padx=30)
            
            # The Dotted Separator line
            ctk.CTkLabel(scroll, text="." * 160, text_color="gray").pack(pady=10)


class AdminPanelFrame(ctk.CTkFrame):
    def __init__(self, master, commands, win_width=None, **kwargs):
        # Store these locally first
        self.win_width = win_width
        self.commands = commands
        # Initialize the frame WITHOUT commands/win_width in kwargs
        super().__init__(master, corner_radius=20, **kwargs)
        ctk.CTkLabel(self, text="ADMIN CONTROL PANEL", 
                     font=("Segoe UI", 24, "bold"), 
                     text_color="#FF9800").pack(pady=30, padx=20)
        # Adjust button width based on screen size
        # Added safety check for win_width if it's None
        current_width = win_width if win_width else 800
        btn_w = 300 if current_width > 600 else 240
        
        ctk.CTkButton(self, text="➕ ADD NEW QUESTION", width=btn_w, height=50, 
                      command=self.commands['add']).pack(pady=10, padx=40)
        
        ctk.CTkButton(self, text="📋 MANAGE QUESTIONS", width=btn_w, height=50, 
                      fg_color="#3B8ED0", command=self.commands['manage']).pack(pady=10, padx=40)
        
        ctk.CTkButton(self, text="👥 MANAGE USERS", width=btn_w, height=50, 
                      fg_color="#3B8ED0", command=self.commands['users']).pack(pady=10, padx=40)
        
        ctk.CTkButton(self, text="⬅ BACK TO DASHBOARD", fg_color="gray", 
                      width=btn_w, height=40, command=self.commands['back']).pack(pady=20, padx=40)
        
        
class UserManagementFrame(ctk.CTkFrame):
    def __init__(self, master, search_query, users_list, commands, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(header, text="⬅ BACK", width=100, fg_color="#3498db", 
                      command=commands['back']).pack(side="left", padx=(0, 20))
        
        search_entry = ctk.CTkEntry(header, placeholder_text="Search users...", width=250)
        search_entry.pack(side="left", padx=5)
        
        if search_query: 
            search_entry.insert(0, search_query)
            
        ctk.CTkButton(header, text="🔍 SEARCH", width=80, 
                      command=lambda: commands['search'](search_entry.get())).pack(side="left", padx=5)
        
        ctk.CTkButton(header, text="➕ ADD NEW ADMIN", fg_color="#4CAF50", hover_color="#388E3C", 
                      command=commands['add_admin']).pack(side="right")
        
        container = ctk.CTkScrollableFrame(main_frame, label_text="REGISTERED USERS")
        container.pack(expand=True, fill="both")

        for username, is_admin in users_list:
            row_frame = ctk.CTkFrame(container)
            row_frame.pack(fill="x", padx=10, pady=5)
            
            status_text = " [ADMIN]" if is_admin else ""
            status_color = "#9C27B0" if is_admin else "white"
            
            ctk.CTkLabel(row_frame, text=f"User: {username}", font=("Arial", 14, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(row_frame, text=status_text, text_color=status_color).pack(side="left")
            
            ctk.CTkButton(row_frame, text="DELETE", width=80, fg_color="#FF5252", hover_color="#D32F2F", 
                          command=lambda u=username: commands['delete'](u)).pack(side="right", padx=5)
            
            ctk.CTkButton(row_frame, text="Reset Password", width=120, 
                          command=lambda u=username: commands['reset'](u)).pack(side="right", padx=5)
            

class ManageQuestionsFrame(ctk.CTkFrame):
    def __init__(self, master, back_cmd, refresh_cmd, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        # 1. Top Bar
        top_bar = ctk.CTkFrame(self, height=80)
        top_bar.pack(side="top", fill="x", padx=20, pady=10)
        top_bar.pack_propagate(False) 
        
        ctk.CTkButton(top_bar, text="⬅ BACK", width=100, height=40, 
                      command=back_cmd).pack(side="left", padx=10)
        
        ctk.CTkLabel(top_bar, text="MANAGE DATABASE", 
                     font=("Segoe UI", 22, "bold")).pack(side="left", padx=20)
        
        # 2. Search Container
        search_container = ctk.CTkFrame(top_bar, fg_color="transparent")
        search_container.pack(side="right", padx=30)
        self.search_var = ctk.StringVar()
        # The trace calls the refresh command whenever the user types
        self.search_var.trace_add("write", lambda *args: refresh_cmd(self.container, self.search_var.get()))
        search_ent = ctk.CTkEntry(search_container, placeholder_text="🔍 Search questions...", 
                                  width=400, height=40, textvariable=self.search_var)
        search_ent.pack(side="left", padx=(0, 10))
        
        # 3. List Container
        self.container = ctk.CTkScrollableFrame(self, width=1200, height=700)
        self.container.pack(side="top", fill="both", expand=True, padx=20, pady=(0, 20))



class EditQuestionFrame(ctk.CTkFrame):
    def __init__(self, master, q_data, win_width, save_callback, cancel_cmd, **kwargs):
        super().__init__(master, corner_radius=20, **kwargs)
        
        ctk.CTkLabel(self, text="EDIT QUESTION", font=("Segoe UI", 24, "bold"), 
                     text_color="#3498db").pack(pady=20)
        
        ent_w = min(500, win_width - 60)
        q_id = q_data[0] # The rowid

        # Pre-filling the entries with existing data from q_data
        self.cat_e = ctk.CTkEntry(self, placeholder_text="Category", width=ent_w)
        self.cat_e.pack(pady=5, padx=20); self.cat_e.insert(0, q_data[1])
        
        self.sub_e = ctk.CTkEntry(self, placeholder_text="Subject", width=ent_w)
        self.sub_e.pack(pady=5, padx=20); self.sub_e.insert(0, q_data[2])
        
        ctk.CTkLabel(self, text="Question Text:", font=("Segoe UI", 13, "italic"), 
                     text_color="gray").pack(anchor="w", padx=20)
        
        self.q_e = ctk.CTkTextbox(self, width=ent_w, height=120, border_width=2)
        self.q_e.pack(pady=5, padx=20); self.q_e.insert("0.0", q_data[3])
        
        # Options
        self.opts = []
        for i in range(4):
            opt = ctk.CTkEntry(self, placeholder_text=f"Option {i+1}", width=ent_w)
            opt.pack(pady=5, padx=20)
            opt.insert(0, q_data[4+i])
            self.opts.append(opt)
        
        self.ans_e = ctk.CTkEntry(self, placeholder_text="Correct Answer", width=ent_w)
        self.ans_e.pack(pady=5, padx=20); self.ans_e.insert(0, q_data[8])
        
        # We pass the collected data back to the save_callback in main.py
        def on_save():
            save_callback(
                q_id, 
                self.cat_e.get(), 
                self.sub_e.get(), 
                self.q_e.get("0.0", "end-1c").strip(),
                [o.get() for o in self.opts],
                self.ans_e.get()
            )

        ctk.CTkButton(self, text="SAVE CHANGES", fg_color="#2ecc71", width=ent_w, 
                      height=45, command=on_save).pack(pady=20, padx=20)
        
        ctk.CTkButton(self, text="CANCEL", fg_color="gray", width=ent_w, 
                      command=cancel_cmd).pack(pady=5, padx=20)
        


class AddAdminDialog(ctk.CTkToplevel):
    def __init__(self, master, save_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Add Admin")
        self.geometry("400x300")
        self.attributes("-topmost", True)

        ctk.CTkLabel(self, text="Create Admin Account", font=("Arial", 18, "bold")).pack(pady=20)
        
        self.u_ent = ctk.CTkEntry(self, placeholder_text="Admin Username", width=250)
        self.u_ent.pack(pady=10)
        
        self.p_ent = ctk.CTkEntry(self, placeholder_text="Admin Password", width=250, show="*")
        self.p_ent.pack(pady=10)

        # We pass the entries' values back to the main logic
        def on_save():
            save_callback(self.u_ent.get(), self.p_ent.get(), self)

        ctk.CTkButton(self, text="CREATE", command=on_save).pack(pady=20)


class AddQuestionFrame(ctk.CTkFrame):
    def __init__(self, master, win_width, save_callback, cancel_cmd, **kwargs):
        super().__init__(master, corner_radius=20, **kwargs)
        
        ctk.CTkLabel(self, text="ADD NEW MCQ", font=("Segoe UI", 24, "bold"), 
                     text_color="#FF9800").pack(pady=20)
        
        # Calculate dynamic width
        ent_w = min(500, win_width - 60)

        self.cat_e = ctk.CTkEntry(self, placeholder_text="Category", width=ent_w)
        self.cat_e.pack(pady=5, padx=20)
        
        self.sub_e = ctk.CTkEntry(self, placeholder_text="Subject", width=ent_w)
        self.sub_e.pack(pady=5, padx=20)
        
        ctk.CTkLabel(self, text="Question Text:", font=("Segoe UI", 13, "italic"), 
                     text_color="gray").pack(anchor="w", padx=20)
        
        self.q_e = ctk.CTkTextbox(self, width=ent_w, height=120, border_width=2)
        self.q_e.pack(pady=5, padx=20)
        
        self.opts = [ctk.CTkEntry(self, placeholder_text=f"Option {i}", width=ent_w) for i in range(1, 5)]
        for o in self.opts: 
            o.pack(pady=5, padx=20)
        
        self.ans_e = ctk.CTkEntry(self, placeholder_text="Correct Answer", width=ent_w)
        self.ans_e.pack(pady=5, padx=20)
        
        def on_save():
            # Pass all entry values to the save logic in main.py
            save_callback(
                self.cat_e.get(),
                self.sub_e.get(),
                self.q_e.get("0.0", "end-1c").strip(),
                [o.get() for o in self.opts],
                self.ans_e.get()
            )

        ctk.CTkButton(self, text="SAVE TO DATABASE", fg_color="green", width=ent_w, 
                      height=45, command=on_save).pack(pady=20, padx=20)
        
        ctk.CTkButton(self, text="CANCEL", fg_color="gray", width=ent_w, 
                      command=cancel_cmd).pack(pady=5, padx=20)


class ProgressFrame(ctk.CTkFrame):
    def __init__(self, master, progress_df, back_cmd, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        ctk.CTkButton(self, text="⬅ BACK", command=back_cmd).pack(pady=10)
        ctk.CTkLabel(self, text="PERFORMANCE GRAPH", font=("Segoe UI", 32, "bold"), text_color="#3B8ED0").pack(pady=20)
        
        container = ctk.CTkFrame(self, corner_radius=20)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        if progress_df is not None and not progress_df.empty:
            try:
                # Reverse to get chronological order (oldest to newest)
                df = progress_df.iloc[::-1].copy() 
                
                fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
                fig.patch.set_alpha(0.0) 
                
                # Use number of quizzes for the x-axis
                # This prevents the vertical line "n" issue
                x_values = list(range(1, len(df) + 1))
                ax.plot(x_values, df['percentage'], marker='o', color='#3B8ED0', linewidth=3)
                
                ax.set_ylim(0, 105)
                ax.set_xticks(x_values) # Show 1, 2, 3... on the bottom
                ax.set_xlabel("Quiz Number")
                ax.set_ylabel("Score %")
                ax.grid(True, linestyle='--', alpha=0.6)
                
                canvas = FigureCanvasTkAgg(fig, master=container)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
            except:
                pass
        else:
            ctk.CTkLabel(container, text="No quiz history yet. Take a quiz to see progress!").pack(expand=True)


class WeakSubjectFrame(ctk.CTkFrame):
    def __init__(self, master, weak_data, back_cmd, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        ctk.CTkButton(self, text="⬅ BACK", command=back_cmd).pack(pady=10)
        ctk.CTkLabel(self, text="WEAKEST SUBJECT", font=("Segoe UI", 32, "bold"), 
                     text_color="#E91E63").pack(pady=40)
        
        card = ctk.CTkFrame(self, corner_radius=20, width=500, height=300)
        card.pack(pady=20)
        card.pack_propagate(False)
        
        # Ensure we check if weak_data has the expected content
        if weak_data and len(weak_data) >= 2:
            ctk.CTkLabel(card, text="You need to improve in:", 
                         font=("Segoe UI", 16)).pack(pady=(70, 10))
            
            # Subject Name
            ctk.CTkLabel(card, text=str(weak_data[0]).upper(), 
                         font=("Segoe UI", 42, "bold"), 
                         text_color="#E91E63").pack()
            
            # Accuracy Percentage
            try:
                acc_val = float(weak_data[1])
                ctk.CTkLabel(card, text=f"Average Accuracy: {acc_val:.1f}%").pack(pady=10)
            except:
                ctk.CTkLabel(card, text=f"Average Accuracy: {weak_data[1]}%").pack(pady=10)
        else:
            # This is what you currently see because the database returned nothing
            ctk.CTkLabel(card, text="Not enough data yet. Complete more quizzes!").pack(expand=True)


class RefreshableQuestionCard:
    @staticmethod
    def create_question_card(parent, container, row):
        # Safety Check: If the container is destroyed, stop immediately
        if not container or not container.winfo_exists():
            return

        # Unpack the row data
        r_id, ques, o1, o2, o3, o4, ans, cat, sub = row
        
        # Build the row frame with a blue border
        f = ctk.CTkFrame(container, border_width=2, border_color="#3498db")
        f.pack(fill="x", pady=10, padx=20)
        
        # Content Container
        content = ctk.CTkFrame(f, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=20, pady=10)

        # Header: ID | Category | Subject 
        header_text = f"ID: {r_id} | {cat} | {sub}"
        ctk.CTkLabel(content, text=header_text, font=("Segoe UI", 13, "bold"), 
                     text_color="#3498db").pack(anchor="w")

        # Question Text
        # Safety check for winfo_width() to prevent Tcl errors during rapid refreshes
        try:
            current_width = parent.root.winfo_width()
            wrap_val = current_width - 300 if current_width > 300 else 600
        except:
            wrap_val = 600

        ctk.CTkLabel(content, text=f"Q: {ques}", font=("Segoe UI", 16, "bold"), 
                     wraplength=max(wrap_val, 600), justify="left").pack(anchor="w", pady=(10, 5))

        # Options
        options_text = f"  1) {o1}  2) {o2}  3) {o3}  4) {o4}"
        ctk.CTkLabel(content, text=options_text, font=("Segoe UI", 12), 
                     text_color="gray", wraplength=max(wrap_val, 600)).pack(anchor="w")

        # Correct Answer
        ctk.CTkLabel(content, text=f"Answer: {ans}", font=("Segoe UI", 13, "bold"), 
                     text_color="green").pack(anchor="w", pady=(10, 0))
        
        # Action Buttons Frame
        btn_frame = ctk.CTkFrame(f, fg_color="transparent")
        btn_frame.pack(side="right", padx=20, pady=10, anchor="s")
        
        # Use the exact row_map structure your old code used
        row_map = (r_id, cat, sub, ques, o1, o2, o3, o4, ans)
        
        ctk.CTkButton(btn_frame, text="EDIT", width=100, fg_color="#3498db", 
                      command=lambda r=row_map: parent.show_edit_question_page(r)).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="DELETE", width=100, fg_color="#E91E63", 
                      command=lambda i=r_id: parent.delete_logic(i)).pack(side="left", padx=5)