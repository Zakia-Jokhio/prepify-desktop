import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import pandas as pd
import sqlite3 
import time
import traceback
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
# Import app modules
import database_manager as db
import auth_manager as auth
import report_generator as report
from ui_components import *


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Prepify (Entry Test Past Paper Quiz Application)")
        self.root.geometry("1280x850")
        self.selected_category_val = "MDCAT"  # Default starting value
        self.current_user = None
        self.is_admin = 0 
        self.quiz_data = pd.DataFrame()
        self.current_q = 0
        self.answers = {} 
        self.timer_running = False
        self._timer_after_id = None
        self.in_quiz_mode = False
        self.last_score = 0
        self.last_total = 0
        self.last_perc = 0.0 
        self.root.bind("<Configure>", self.update_wraplength)
        db.init_db()
        self.refresh_local_data()
        self.show_main_welcome()


    def refresh_local_data(self):
        self.full_df = db.get_questions()


    def clear_screen(self):
    # This loops through everything inside the window and deletes it
        for widget in self.root.winfo_children():
            widget.destroy()
        # Reset references so we don't try to use 'dead' widgets
        self.dash_comp = None


    def stop_timer(self):
        self.timer_running = False
        if hasattr(self, '_timer_after_id') and self._timer_after_id:
            try: self.root.after_cancel(self._timer_after_id)
            except: pass

    # =========================
    # AUTHENTICATION UI
    # =========================
    def show_main_welcome(self):
        self.clear_screen()
        self.in_quiz_mode = False
        # This is your ORIGINAL welcome screen code
        self.welcome_screen = WelcomeFrame(self.root, auth_callback=self.show_auth_screen)
        self.welcome_screen.pack(expand=True, padx=20, pady=20)

    
    def show_auth_screen(self, mode):
        self.clear_screen()
    # 1. Setup the scrollable container
        scroll = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        scroll.pack(expand=True, fill="both")
    # 2. Initialize the Auth Component
    # We pass the input-handling methods and the back-button method
        self.auth_comp = AuthFrame(
            master=scroll, 
            mode=mode, 
            login_cmd=self.handle_login, 
            register_cmd=self.handle_register, 
            back_cmd=self.show_main_welcome,
            win_width=self.root.winfo_width()
        )
        self.auth_comp.pack(expand=True, pady=40, padx=20)
    # 3. Link original self.auth_user/pass to the component's entries 
    # This ensures your handle_login/register methods don't need any changes!
        self.auth_user = self.auth_comp.auth_user
        self.auth_pass = self.auth_comp.auth_pass


    def handle_login(self):
        u, p = self.auth_user.get(), self.auth_pass.get()
        success, is_admin, logged_in_user = auth.handle_login_db(u, p)
        if success:
        # Save these to the main class so they are never "forgotten"
            self.current_user = logged_in_user
            self.is_admin = is_admin
        # FIX: Define the missing attribute. 
            # We use 'u' (the username) as the unique identifier for the database
            self.current_user_id = u 
            # Now call it using the saved data
            self.show_dashboard(self.is_admin, self.current_user)
        else:
            messagebox.showerror("Error", "Invalid credentials")


    def handle_register(self):
        if auth.handle_register_db(self.auth_user.get(), self.auth_pass.get()):
            messagebox.showinfo("Success", "Account created!"); self.show_auth_screen("login")
        else: messagebox.showerror("Error", "Username exists")

    # =========================
    # DASHBOARD & QUIZ ENGINE
    # =========================

    def show_dashboard(self, is_admin=0, user_name="Guest"):
    # 1. Fetch data using the correct username
        user_stats = db.get_user_dashboard_data(self.current_user_id)
        recent_history = db.get_recent_activity(self.current_user_id)
        self.clear_screen()
        self.in_quiz_mode = False
        categories = list(self.full_df['Category'].unique())
        subjects = sorted(self.full_df['Subject'].unique())
        cmds = {
            'admin': self.show_admin_panel,
            'progress': self.show_progress_view,
            'weak': self.show_weakest_subject_view,
            'logout': self.show_main_welcome,
            'dash_cmd': self.show_dashboard, 
            'start': self.start_quiz
        }
    # 2. Building the Frame
        self.dash_comp = DashboardFrame(
            master=self.root,
            is_admin=is_admin,
            user_name=user_name, 
            categories=categories,
            subjects_df=self.full_df, 
            subjects=subjects,
            commands=cmds,
            stats_data=user_stats, 
            win_width=self.root.winfo_width()
        )
        self.dash_comp.pack(fill="both", expand=True)


    def update_app_category(self, choice):
        self.selected_category_val = choice


    def start_quiz(self):
    # 1. Get current values from the Dashboard component (dash_comp)
        cat = self.dash_comp.cat_cb.get()
        count = self.dash_comp.num_ent.get()
        print(f"Starting quiz for category: {self.selected_category_val}")
        # Access subject_vars from dash_comp
        subs = [s for s, v in self.dash_comp.subject_vars.items() if v.get()]
        # Get the mode from your Dashboard component
        # We use getattr to safely default to "Classic" if the variable isn't found
        self.quiz_mode = getattr(self.dash_comp, 'mode_var', ctk.StringVar(value="Classic")).get()
    # 2. CHECK FOR EMPTY FIELDS 
        if not cat or cat == "Select Category" or not subs or not count:
            messagebox.showwarning("Missing Information", 
                                "Please select a Category, at least one Subject, and enter the Number of Questions.")
            return
    # 3. Basic validation for digits
        if not count.isdigit(): 
            messagebox.showerror("Invalid Input", "Please enter a valid number for the question count.")
            return
    # 4. Filter data based on selections
        filtered = self.full_df[(self.full_df['Category'] == cat) & (self.full_df['Subject'].isin(subs))]
        available_count = len(filtered)
    # 5. CHECK FOR INSUFFICIENT QUESTIONS
        if int(count) > available_count:
            msg = f"Only {available_count} questions are available for these selections.\n\nStart with all {available_count} questions?"
            if messagebox.askyesno("Question Limit", msg):
                count = available_count
            else:
                return
    # 6. Start Quiz Logic 
        if int(count) <= 0: return 
        # Mode-Specific Settings
        final_count = int(count)
        if self.quiz_mode == "Sprint":
            multiplier = 10  # 10 seconds per question
        else:
            multiplier = 60  # Your original 60 seconds per question

        self.quiz_data = filtered.sample(n=final_count).reset_index(drop=True)
        self.time_left = len(self.quiz_data) * multiplier
        self.current_q, self.answers = 0, {}
        self.timer_running = True
        self.start_time = time.time()
        self.show_quiz_ui()
        self.update_timer()


    def update_timer(self):
        if self.timer_running and self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            # This line shows the timer label
            self.timer_label.configure(text=f"Time Remaining: {mins:02d}:{secs:02d}")
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        elif self.time_left <= 0:
            self.finish_quiz()


    def show_quiz_ui(self):
    # Clear screens
        for widget in self.root.winfo_children(): 
            if widget != getattr(self, 'sidebar', None): widget.destroy()
    # Initialize current question data
        q_data = self.quiz_data.iloc[self.current_q]
        saved_ans = self.answers.get(self.current_q, "None")
    # Initialize the Quiz Component
        self.quiz_comp = QuizFrame(
            master=self.root,
            current_q=self.current_q,
            total_q=len(self.quiz_data),
            question_data=q_data,
            saved_answer=saved_ans,
            next_cmd=self.handle_next,
            prev_cmd=self.prev_q
        )
        self.quiz_comp.pack(side="right", fill="both", expand=True)
        self.timer_label = self.quiz_comp.timer_label
        self.opt_var = self.quiz_comp.opt_var


    def handle_next(self):
    # Get user selection from radio buttons
        selected_option = self.opt_var.get()
        self.answers[self.current_q] = selected_option
    # SUDDEN DEATH MODE CHECK
        if hasattr(self, 'quiz_mode') and self.quiz_mode == "Death":
            correct_ans = str(self.quiz_data.iloc[self.current_q]['Answer'])
            if selected_option != correct_ans:
                messagebox.showinfo("ELIMINATED", "Incorrect! In Sudden Death mode, one mistake ends the quiz.")
                self.finish_quiz()
                return
    # NAVIGATION LOGIC 
        if self.current_q < len(self.quiz_data) - 1: 
            self.current_q += 1
            self.show_quiz_ui()
        else: 
            self.finish_quiz()


    def prev_q(self): self.answers[self.current_q] = self.opt_var.get(); self.current_q -= 1; self.show_quiz_ui()


    def finish_quiz(self):
        self.stop_timer() 
        try:
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        # 1. Calculate the stats
            f_score = sum(1 for i, q in self.quiz_data.iterrows() 
                            if str(self.answers.get(i)) == str(q["Answer"]))
            f_total = len(self.quiz_data)
            f_perc = (f_score / f_total) * 100
        # 2. Update class variables for safety
            self.last_score = f_score
            self.last_total = f_total
            self.last_perc = f_perc
       # 3. Save to database (Confirmed working for spceific username!)
            try:
                final_cat = self.dash_comp.cat_cb.get() 
            except:
        # Fallback if the dashboard isn't loaded
                final_cat = "MDCAT"
            db.save_quiz_results(
                db,
                self.current_user,                        # 1. user
                f_score,                                  # 2. score
                f_total,                                  # 3. total
                f_perc,                                   # 4. percentage
                final_cat,                                # 5. category          
                ts,                                       # 6. timestamp
                self.quiz_data,                           # 7. quiz_data
                self.answers                              # 8. answers 
            )
            print(f"DEBUG: Successfully saved. Passing {f_score}, {f_total}, {f_perc} to results.")
        # 4. THE KEY FIX: Pass the 3 missing arguments into the method
            self.show_results(f_score, f_total, f_perc)
        except Exception as e:
            print(f"CRITICAL ERROR in finish_quiz: {e}")
            traceback.print_exc()
            # Fallback to dashboard if results page fails to load
            self.show_dashboard(self.is_admin, self.current_user)


    def show_results(self, final_score, total_q, perc):
        """Handles only the UI display of results."""
        self.clear_screen()
    # 1. Refresh the local data so the app knows about the quiz we just finished
        self.refresh_local_data() 

        self.results_comp = ResultsFrame(
            master=self.root,
            last_score=self.last_score,
            last_total=self.last_total,
            report_module=report, 
            review_cmd=lambda: self.show_review(),
        # 2. Refresh before going to dashboard
            dash_cmd=lambda: self.reload_dashboard_with_data()
        )
        self.results_comp.pack(fill="both", expand=True)


    def reload_dashboard_with_data(self):
        """Helper to ensure data is fresh before showing the dashboard."""
        self.refresh_local_data()
        self.show_dashboard(self.is_admin, self.current_user)


    def back_to_results(self):
        """Helper method for buttons to return to results without arguments."""
        # This pulls the data we saved in finish_quiz
        self.show_results(self.last_score, self.last_total, self.last_perc)


    def show_review(self):
        self.clear_screen()
        self.review_page = ReviewFrame(
            master=self.root,
            quiz_data=self.quiz_data,
            answers=self.answers,
            back_cmd=self.back_to_results,
            save_cmd=lambda: report.save_quiz_pdf(
                None,                           # ignored_path
                self.current_user,              # user
                self.selected_category_val,     # category
                self.last_score,                # score
                self.last_total,                # total
                self.start_time,                # start_time
                self.quiz_data,                 # quiz_data
                self.answers                    # answers
            )
        )
        self.review_page.pack(fill="both", expand=True)


    def save_pdf(self):
        # We pass None for the path since the logic finds 'Downloads' automatically
        report.save_quiz_pdf(None, self.current_user, self.cat_cb.get(), 
                             self.last_score, self.last_total, 
                             self.start_time, self.quiz_data, self.answers)
        
    # =========================
    # ADMIN & ANALYTICS
    # =========================
    def show_admin_panel(self):
        self.clear_screen()
    # 1. Setup the scrollable container
        scroll = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        scroll.pack(expand=True, fill="both")
    # 2. Map administrative commands
        admin_cmds = {
            'add': self.show_add_question_page,
            'manage': self.show_manage_questions_page,
            'users': self.show_user_management,
            # FIX: Added lambda: here so it doesn't run immediately
            'back': lambda: self.show_dashboard(self.is_admin, self.current_user)
        }
    # 3. Initialize the Admin Component
        self.admin_comp = AdminPanelFrame(
            master=scroll,
            win_width=self.root.winfo_width(),
            commands=admin_cmds
        )
        self.admin_comp.pack(expand=True, pady=40, padx=20)


    def show_user_management(self, search_query=""):
        self.clear_screen()
    # 1. Fetch data logic
        users = db.get_users_list(self.current_user, search_query)
    # 2. Map commands
        user_cmds = {
            'back': self.show_admin_panel,
            'search': self.show_user_management,
            'add_admin': self.add_new_admin_dialog,
            'delete': self.delete_user,
            'reset': self.reset_user_password
        }
    # 3. Initialize Component
        self.user_manage_comp = UserManagementFrame(
            master=self.root,
            search_query=search_query,
            users_list=users,
            commands=user_cmds
        )
        self.user_manage_comp.pack(expand=True, fill="both")


    def show_manage_questions_page(self):
        self.clear_screen()
    # Initialize the Manage Questions Component
    # We pass refresh_manage_list so the search bar can trigger it
        self.manage_comp = ManageQuestionsFrame(
            master=self.root,
            back_cmd=self.show_admin_panel,
            refresh_cmd=self.refresh_manage_list
        )
        self.manage_comp.pack(fill="both", expand=True)
    # Initial load of the question list
        self.refresh_manage_list(self.manage_comp.container, "")


    def refresh_manage_list(self, container=None, search_query=""):
        # 1. Use the provided container or the default one
        target_container = container if container else self.q_cont
        
        # 2. Safety Check: Stop if the UI element doesn't exist
        if not target_container or not target_container.winfo_exists():
            return

        # 3. Clear ONLY the cards inside the container (DO NOT use self.clear_screen())
        for widget in target_container.winfo_children():
            widget.destroy()

        # 4. Get data (using the search-enabled database function)
        rows = db.get_managed_questions(search_query) 
        
        # 5. Show a message if no questions exist
        if not rows:
            ctk.CTkLabel(target_container, text="No questions found.").pack(pady=20)
            return

        # 6. Build the UI cards
        for row in rows:
            if not target_container.winfo_exists():
                break
            # This uses the fancy blue-bordered card we fixed earlier
            RefreshableQuestionCard.create_question_card(self, target_container, row)

            
    def show_edit_question_page(self, q_data):
        self.clear_screen()
        scroll = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        scroll.pack(expand=True, fill="both")

    # Define the save logic that will be called by the component
        def save_changes(q_id, cat, sub, q_text, options, ans):
            success = db.update_question(
                q_id, cat, sub, q_text,
                options[0], options[1], options[2], options[3],
                ans
            )
            if success:
                self.refresh_local_data()
                messagebox.showinfo("Success", "Question Updated Successfully!")
                self.show_manage_questions_page()
            else:
                messagebox.showerror("Error", "Failed to update question.")

    # Initialize the Component
        self.edit_comp = EditQuestionFrame(
            master=scroll,
            q_data=q_data,
            win_width=self.root.winfo_width(),
            save_callback=save_changes,
            cancel_cmd=self.show_manage_questions_page
        )
        self.edit_comp.pack(pady=20, padx=20, expand=True)


    def add_new_admin_dialog(self):
        def save_admin_logic(u, p, dialog_instance):
            if u and p:
            # Logic stays here in main or calls auth module
                if auth.add_admin_db(u, p): 
                    messagebox.showinfo("Success", f"Admin {u} created!")
                    dialog_instance.destroy()
                    self.show_user_management() # Refresh the list
                else:
                    messagebox.showerror("Error", "Could not create admin.")
            else:
                messagebox.showwarning("Input Error", "All fields required")
    # Initialize the UI component
        AddAdminDialog(self.root, save_callback=save_admin_logic)


    def delete_logic(self, q_id):
        if messagebox.askyesno("Confirm", "Delete permanently?"):
            # Modular Call: Logic moved to database_manager.py
            if db.delete_question_by_id(q_id):
                self.refresh_local_data()
                self.show_manage_questions_page()
            else:
                messagebox.showerror("Error", "Could not delete the question.")


    def show_add_question_page(self):
        self.clear_screen()
        scroll = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        scroll.pack(expand=True, fill="both")

        def save_logic(cat, sub, q_text, options, ans):
            if not q_text or not cat or not sub: 
                return
        # Calls the function in your database_manager.py
            success = db.add_new_question(
                cat, sub, q_text, 
                options[0], options[1], options[2], options[3], 
                ans
            )
            if success:
                self.refresh_local_data()
                messagebox.showinfo("Success", "MCQ Saved!")
                self.show_admin_panel()
            else:
                messagebox.showerror("Error", "Failed to save question.")

    # Initialize the Component
        self.add_q_comp = AddQuestionFrame(
            master=scroll,
            win_width=self.root.winfo_width(),
            save_callback=save_logic,
            cancel_cmd=self.show_admin_panel
        )
        self.add_q_comp.pack(pady=20, padx=20, expand=True)


    def delete_user(self, username):
        """UI handler for deleting a user account."""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete user '{username}'?"):
            if auth.delete_user_from_db(username):
                messagebox.showinfo("Deleted", f"User {username} has been removed.")
                self.show_user_management() # Refresh the list
            else:
                messagebox.showerror("Error", "Could not delete user.")


    def reset_user_password(self, username):
        """UI handler for resetting a user's password via a dialog."""
        new_pass = ctk.CTkInputDialog(text=f"Enter new password for {username}:", title="Reset Password").get_input()
        if new_pass:
            if auth.reset_password_in_db(username, new_pass):
                messagebox.showinfo("Success", f"Password updated for {username}.")
            else:
                messagebox.showerror("Error", "Could not update password.")


    def show_progress_view(self):
        self.clear_screen() # This properly removes the Dashboard
        try:
            df = db.get_progress_data(self.current_user_id)
        except:
            df = None 
        self.progress_comp = ProgressFrame(
            master=self.root,
            progress_df=df,
            # FIX: Added lambda here to prevent auto-executing on load
            back_cmd=lambda: self.show_dashboard(self.is_admin, self.current_user_id)
        )
        self.progress_comp.pack(expand=True, fill="both", padx=30)


    def show_weakest_subject_view(self):
        self.clear_screen()
        # Logic: Database Fetch
        try:
            # CHANGE self.current_user TO self.current_user_id
            # This matches the variable set during login
            weak = db.get_weakest_subject_data(self.current_user_id) 
        except Exception as e:
            print(f"Debug: Database fetch failed: {e}")
            weak = None

        # Initialize Component
        self.weak_comp = WeakSubjectFrame(
            master=self.root,
            weak_data=weak,
            # Ensure back_cmd also uses current_user_id
            back_cmd=lambda: self.show_dashboard(self.is_admin, self.current_user_id)
        )
        self.weak_comp.pack(expand=True, fill="both", padx=30)


    def update_wraplength(self, event=None):
        """Safely updates the wraplength only if the widget exists."""
        try:
            # Check if the attribute exists AND the widget itself hasn't been destroyed
            if hasattr(self, 'question_label') and self.question_label.winfo_exists():
                new_width = self.root.winfo_width() - 100
                # Ensure width is at least a reasonable number
                if new_width > 100:
                    self.question_label.configure(wraplength=new_width)
        except Exception:
            # Silently ignore errors if the widget is in the middle of being destroyed
            pass


    def on_closing(self):
        """Cleanly destroys the window and cancels background tasks"""
        # Stops any background 'after' events
        self.root.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = ctk.CTk(); app = QuizApp(root)
    app.root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()