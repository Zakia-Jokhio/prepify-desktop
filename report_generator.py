import os
import time
import textwrap
from datetime import datetime
from pathlib import Path  # import for finding Downloads folder
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def save_quiz_pdf(ignored_path, user, cat, score, total, start_time, quiz_data, answers):
    # 1. FIND DOWNLOADS FOLDER AUTOMATICALLY
    downloads_path = str(Path.home() / "Downloads")
    
    # 2. PREDEFINED NAME LOGIC
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Quiz_Report_{user}_{timestamp}.pdf"
    file_path = os.path.join(downloads_path, filename)

    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    y = 740 

    # --- HEADER SECTION (Matches Reference) ---
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, y, "PREPIFY QUIZ REVIEW REPORT")
    
    y -= 45
    c.setFont("Helvetica-Bold", 13)
    c.drawString(60, y, f"User: {user}")
    
    now = datetime.now()
    c.drawRightString(540, y, f"Date: {now.strftime('%Y-%m-%d')}")
    
    y -= 18
    c.setFont("Helvetica", 11)
    c.drawString(60, y, f"Category: {cat}")
    c.drawRightString(540, y, f"Submission Time: {now.strftime('%H:%M:%S')}")
    
    y -= 18
    duration_secs = int(time.time() - start_time)
    m, s = divmod(duration_secs, 60)
    c.drawString(60, y, f"Score: {score}/{total}  |  Duration: {m:02d}:{s:02d}")
    
    y -= 12
    c.setLineWidth(1)
    c.line(60, y, 540, y)
    
    # --- QUESTIONS SECTION ---
    y -= 30
    for i, q in quiz_data.iterrows():
        if y < 150: 
            c.showPage()
            y = 750

        u_ans = answers.get(i, "None")
        cor_ans = str(q['Answer'])
        is_correct = str(u_ans).strip().lower() == cor_ans.strip().lower()

        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, y, f"Q{i+1}:")
        
        question_text = str(q['Question'])
        wrapped_q = textwrap.wrap(question_text, width=80)
        
        c.setFont("Helvetica", 11)
        for line in wrapped_q:
            c.drawString(85, y, line)
            y -= 15
        
        y -= 5 
        
        c.setFont("Helvetica-Bold", 10)
        if is_correct: 
            c.setFillColor(colors.green)
            c.drawString(85, y, f"Your Answer: {u_ans} [CORRECT]")
            y -= 25
        else: 
            c.setFillColor(colors.red)
            c.drawString(85, y, f"Your Answer: {u_ans}")
            y -= 15
            c.setFillColor(colors.green)
            c.drawString(85, y, f"Correct Answer: {cor_ans}")
            y -= 25
            
        # Dotted line separator between questions
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.5)
        c.setDash(1, 2) 
        c.line(85, y + 10, 540, y + 10)
        c.setDash() 
        
        c.setFillColor(colors.black)
        y -= 15

    c.save()
    
    # 3. SUCCESS MESSAGE
    messagebox.showinfo("Success", f"Quiz Report saved successfully!\n\nFile: {filename}\nLocation: Downloads folder")


def generate_pie_chart(parent, score, total, appearance_mode):
    plt.close('all')
    # 1. Force the figure to use the exact grey background color of your card
    # Light mode grey: #ebebeb | Dark mode grey: #2b2b2b
    bg_hex = "#ebebeb" if appearance_mode.lower() == "light" else "#2b2b2b"
    
    # Create figure with the specific background color instead of 'none'
    fig, ax = plt.subplots(figsize=(5, 4), dpi=100, facecolor=bg_hex)
    ax.set_facecolor(bg_hex)
    
    labels = ['Correct', 'Incorrect']
    sizes = [score, total - score]
    
    # Set text color based on mode
    text_col = "black" if appearance_mode.lower() == "light" else "white"
    
    # Draw the pie
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
           colors=['#4CAF50', '#E91E63'], 
           textprops={'color': text_col, 'fontsize': 10})
    
    ax.axis('equal')
    plt.tight_layout(pad=2.0)
    
    canvas_obj = FigureCanvasTkAgg(fig, master=parent)
    canvas_widget = canvas_obj.get_tk_widget()

    # 2. Force the Tkinter widget to match the same color and remove borders
    canvas_widget.configure(
        bg=bg_hex, 
        highlightthickness=0, 
        borderwidth=0
    )
    
    return canvas_obj

