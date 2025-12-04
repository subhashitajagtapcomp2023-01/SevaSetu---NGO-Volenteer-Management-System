import tkinter as tk
from tkinter import ttk, messagebox
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

API_URL = "http://127.0.0.1:5001"

# ------------------------------
# Helper Functions for API Calls
# ------------------------------
def find_volunteers():
    skill = skill_entry.get().strip()
    district = district_entry.get().strip()

    if not skill:
        messagebox.showwarning("⚠️ Input Required", "Please enter a skill.")
        return

    try:
        response = requests.post(f"{API_URL}/api/skilled_volunteers",
                                 json={"skill": skill, "district": district})
        data = response.json()
        result_box.delete(*result_box.get_children())

        if not data:
            messagebox.showinfo("ℹ️ No Results", "No volunteers found.")
            clear_chart(chart_frame1)
        else:
            for v in data:
                result_box.insert("", "end", values=(v['Volunteer_Name'], v['Primary_Skill'], v['District']))
            df = pd.DataFrame(data)
            plot_skill_distribution(df, chart_frame1)
    except Exception as e:
        messagebox.showerror("❌ Error", f"Failed to fetch data: {e}")

def form_team():
    skill = skill_entry_team.get().strip()
    team_size = team_size_entry.get().strip()

    if not skill:
        messagebox.showwarning("⚠️ Input Required", "Please enter a skill.")
        return

    try:
        response = requests.post(f"{API_URL}/api/form_team",
                                 json={"skill": skill, "team_size": int(team_size)})
        data = response.json()

        team_box.delete(*team_box.get_children())
        if not data:
            clear_chart(chart_frame2)
        else:
            for v in data:
                team_box.insert("", "end", values=(v['Volunteer_Name'], v['Primary_Skill'], v['District']))
            df = pd.DataFrame(data)
            plot_team_composition(df, chart_frame2)
    except Exception as e:
        messagebox.showerror("❌ Error", f"Error forming team: {e}")

def predict_showup():
    feature1 = feature1_entry.get().strip()
    feature2 = feature2_entry.get().strip()
    feature3 = feature3_entry.get().strip()

    if not (feature1 and feature2 and feature3):
        messagebox.showwarning("⚠️ Input Required", "Enter all three volunteer features.")
        return

    try:
        response = requests.post(f"{API_URL}/api/showup_prediction",
                                 json={"volunteer_features": [feature1, feature2, feature3]})
        data = response.json()
        prediction = data.get('prediction', 0)
        showup_result_label.config(text=f"✅ Prediction: {prediction}", fg="#00796b")
        plot_showup_prediction(prediction, chart_frame3)
    except Exception as e:
        messagebox.showerror("❌ Error", f"Failed to predict: {e}")

def recommend_volunteers():
    try:
        n = int(recommend_entry.get().strip() or 5)
        response = requests.post(f"{API_URL}/api/recommend_volunteers", json={"top_n": n})
        data = response.json()

        rec_box.delete(*rec_box.get_children())
        if not data:
            clear_chart(chart_frame4)
        else:
            for v in data:
                rec_box.insert("", "end", values=(v['Volunteer_Name'], v['Primary_Skill'], v['District']))
            df = pd.DataFrame(data)
            plot_recommendations(df, chart_frame4)
    except Exception as e:
        messagebox.showerror("❌ Error", f"Failed to recommend volunteers: {e}")

def show_skill_gap():
    try:
        response = requests.get(f"{API_URL}/api/skill_gap")
        data = response.json()
        skill_gap_text.delete(1.0, tk.END)
        if data:
            for skill, suggestion in data.items():
                skill_gap_text.insert(tk.END, f"🌱 {skill} → {suggestion}\n")
            df = pd.DataFrame(list(data.items()), columns=["Skill","Suggestion"])
            plot_skill_gap(df, chart_frame5)
        else:
            clear_chart(chart_frame5)
    except Exception as e:
        messagebox.showerror("❌ Error", f"Error loading skill gap info: {e}")

def feedback_recommendations():
    try:
        response = requests.post(f"{API_URL}/api/feedback_recommendations", json={})
        data = response.json()
        feedback_text.delete(1.0, tk.END)
        if data.get("recommendations"):
            for rec in data["recommendations"]:
                feedback_text.insert(tk.END, f"⭐ {rec}\n")
        else:
            feedback_text.insert(tk.END, "No recommendations available.")
    except Exception as e:
        messagebox.showerror("❌ Error", f"Failed to load feedback recommendations: {e}")

def volunteer_engagement():
    volunteer_id = volunteer_id_entry.get().strip()
    if not volunteer_id:
        messagebox.showwarning("⚠️ Input Required", "Enter a Volunteer ID.")
        return

    try:
        response = requests.get(f"{API_URL}/api/volunteer_engagement/{volunteer_id}")
        data = response.json()
        engagement_label.config(
            text=f"🕒 Hours Logged: {data['hours_logged']} | 🎯 Events Participated: {data['events_participated']}",
            fg="#004d40"
        )
        plot_engagement(data, chart_frame5b)
    except Exception as e:
        messagebox.showerror("❌ Error", f"Error fetching engagement data: {e}")

def training_suggestions():
    volunteer_id = training_volunteer_id.get().strip()
    if not volunteer_id:
        messagebox.showwarning("⚠️ Input Required", "Enter a Volunteer ID.")
        return

    try:
        response = requests.get(f"{API_URL}/api/training_suggestions/{volunteer_id}")
        data = response.json()
        training_text.delete(1.0, tk.END)
        if data.get("suggestions"):
            for s in data["suggestions"]:
                training_text.insert(tk.END, f"🎓 {s}\n")
        else:
            training_text.insert(tk.END, "No training suggestions available.")
    except Exception as e:
        messagebox.showerror("❌ Error", f"Error fetching training suggestions: {e}")

# ------------------------------
# Chart Utility Functions
# ------------------------------
def clear_chart(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def plot_skill_distribution(df, frame):
    clear_chart(frame)
    fig, ax = plt.subplots(figsize=(5,3))
    counts = df['Primary_Skill'].value_counts()
    ax.bar(counts.index, counts.values, color="#80cbc4")
    ax.set_title("Volunteers per Skill")
    ax.set_ylabel("Count")
    ax.set_xticklabels(counts.index, rotation=45, ha="right")
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def plot_team_composition(df, frame):
    clear_chart(frame)
    fig, ax = plt.subplots(figsize=(5,3))
    counts = df['Primary_Skill'].value_counts()
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90, colors=plt.cm.Pastel1.colors)
    ax.set_title("Team Skill Composition")
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def plot_showup_prediction(prediction, frame):
    clear_chart(frame)
    fig, ax = plt.subplots(figsize=(5,2))
    ax.bar(["Prediction"], [prediction], color="#80cbc4")
    ax.set_ylim(0,100)
    ax.set_ylabel("Attendance Probability (%)")
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def plot_recommendations(df, frame):
    clear_chart(frame)
    fig, ax = plt.subplots(figsize=(5,3))
    names = df['Volunteer_Name']
    ax.barh(names, range(len(names),0,-1), color="#80cbc4")
    ax.set_title("Top Recommended Volunteers")
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def plot_skill_gap(df, frame):
    clear_chart(frame)
    fig, ax = plt.subplots(figsize=(5,3))
    ax.barh(df['Skill'], range(len(df),0,-1), color="#80cbc4")
    ax.set_title("Skill Gap Analysis")
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def plot_engagement(data, frame):
    clear_chart(frame)
    fig, ax = plt.subplots(figsize=(5,3))
    ax.bar(["Hours Logged", "Events Participated"], [data['hours_logged'], data['events_participated']], color="#80cbc4")
    ax.set_title("Volunteer Engagement")
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# ------------------------------
# GUI Setup
# ------------------------------
root = tk.Tk()
root.title("🌍 SEVASETU")
root.geometry("950x800")
root.config(bg="#e8f5e9")

# Header
title = tk.Label(root, text="🤝 NGO Volunteer Management System", font=("Helvetica",20,"bold"),
                 bg="#004d40", fg="white", padx=15, pady=15)
title.pack(fill="x")

# ------------------------------
# Home Page
# ------------------------------
def show_main_app(tab_index=0):
    home_frame.pack_forget()
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    notebook.select(tab_index)

home_frame = tk.Frame(root, bg="#e0f7fa")
home_frame.pack(fill="both", expand=True)

welcome_label = tk.Label(home_frame, text="🌍 Welcome to SEVASETU",
                         font=("Helvetica",28,"bold"), bg="#e0f7fa", fg="#004d40", pady=20)
welcome_label.pack()

intro_label = tk.Label(home_frame, text="Manage volunteers, form teams, predict attendance, and track engagement—all in one place!",
                       font=("Arial",14), bg="#e0f7fa", fg="#004d40", wraplength=800, justify="center")
intro_label.pack(pady=10)

cards_frame = tk.Frame(home_frame, bg="#e0f7fa")
cards_frame.pack(pady=30)

features = [
    ("🔍 Find Volunteers", "Search volunteers by skill & district", 0),
    ("👥 Form Teams", "Auto-create teams based on skill & size", 1),
    ("📊 Show-up Prediction", "Predict volunteer attendance", 2),
    ("🌟 Recommendations", "Get top volunteers for events", 3),
    ("🌱 Skill Gap Analysis", "Identify missing skills & training", 4),
]

for i, (title_text, desc_text, tab_idx) in enumerate(features):
    card = tk.Frame(cards_frame, bg="white", bd=2, relief="raised", width=200, height=100)
    card.grid(row=i//2, column=i%2, padx=15, pady=15)
    card.pack_propagate(False)
    tk.Label(card, text=title_text, font=("Arial",12,"bold"), bg="white").pack(pady=5)
    tk.Label(card, text=desc_text, font=("Arial",10), bg="white", wraplength=180, justify="center").pack(pady=5)
    tk.Button(card, text="Go", bg="#80cbc4", fg="black", command=lambda idx=tab_idx: show_main_app(idx)).pack(pady=5)

# ------------------------------
# Notebook Tabs
# ------------------------------
notebook = ttk.Notebook(root)

# ---- Tab1: Find Volunteers ----
tab1 = tk.Frame(notebook, bg="#ffffff")
notebook.add(tab1, text="🔍 Find Volunteers")
tk.Label(tab1, text="Skill:", bg="white").grid(row=0,column=0,padx=10,pady=5,sticky="w")
skill_entry = tk.Entry(tab1,width=25); skill_entry.grid(row=0,column=1)
tk.Label(tab1, text="District:", bg="white").grid(row=0,column=2,padx=10,pady=5,sticky="w")
district_entry = tk.Entry(tab1,width=25); district_entry.grid(row=0,column=3)
tk.Button(tab1,text="Search", command=find_volunteers, bg="#80cbc4").grid(row=0,column=4,padx=10)

columns=("Volunteer_Name","Primary_Skill","District")
result_box = ttk.Treeview(tab1, columns=columns, show="headings", height=12)
for col in columns:
    result_box.heading(col,text=col)
    result_box.column(col,width=200)
result_box.grid(row=1,column=0,columnspan=5,pady=10)

chart_frame1 = tk.Frame(tab1, bg="white")
chart_frame1.grid(row=2,column=0,columnspan=5,pady=10)

# ---- Tab2: Form Team ----
tab2 = tk.Frame(notebook, bg="white")
notebook.add(tab2, text="👥 Form Team")
tk.Label(tab2, text="Skill:", bg="white").grid(row=0,column=0,padx=10,pady=5)
skill_entry_team = tk.Entry(tab2,width=25); skill_entry_team.grid(row=0,column=1)
tk.Label(tab2, text="Team Size:", bg="white").grid(row=0,column=2,padx=10,pady=5)
team_size_entry = tk.Entry(tab2,width=10); team_size_entry.insert(0,"5"); team_size_entry.grid(row=0,column=3)
tk.Button(tab2, text="Form Team", command=form_team, bg="#80cbc4").grid(row=0,column=4,padx=10)
team_box = ttk.Treeview(tab2, columns=columns, show="headings", height=12)
for col in columns:
    team_box.heading(col,text=col)
    team_box.column(col,width=200)
team_box.grid(row=1,column=0,columnspan=5,pady=10)
chart_frame2 = tk.Frame(tab2,bg="white"); chart_frame2.grid(row=2,column=0,columnspan=5,pady=10)

# ---- Tab3: Show-up Prediction ----
tab3 = tk.Frame(notebook,bg="white")
notebook.add(tab3, text="📊 Show-up Prediction")
feature_labels = ["Availability (Available/Busy)","Attendance Rate (%)","Distance from Event (km)"]
feature_entries=[]
for i,label in enumerate(feature_labels):
    tk.Label(tab3,text=label+":", bg="white").grid(row=i,column=0,padx=10,pady=5,sticky="w")
    entry=tk.Entry(tab3,width=25); entry.grid(row=i,column=1,padx=10,pady=5)
    feature_entries.append(entry)
feature1_entry, feature2_entry, feature3_entry = feature_entries
tk.Button(tab3,text="Predict", command=predict_showup,bg="#80cbc4").grid(row=3,column=0,columnspan=2,pady=10)
showup_result_label = tk.Label(tab3,text="", font=("Arial",12,"bold"), bg="white"); showup_result_label.grid(row=4,column=0,columnspan=2,pady=10)
chart_frame3 = tk.Frame(tab3,bg="white"); chart_frame3.grid(row=5,column=0,columnspan=2,pady=10)

# ---- Tab4: Recommendations ----
tab4 = tk.Frame(notebook,bg="white")
notebook.add(tab4, text="🌟 Recommendations")
tk.Label(tab4,text="Top N Volunteers:", bg="white").grid(row=0,column=0,padx=10,pady=5)
recommend_entry=tk.Entry(tab4,width=10); recommend_entry.insert(0,"5"); recommend_entry.grid(row=0,column=1)
tk.Button(tab4,text="Get Recommendations", command=recommend_volunteers,bg="#80cbc4").grid(row=0,column=2,padx=10)
rec_box = ttk.Treeview(tab4, columns=columns, show="headings", height=12)
for col in columns:
    rec_box.heading(col,text=col); rec_box.column(col,width=200)
rec_box.grid(row=1,column=0,columnspan=4,pady=10)
chart_frame4 = tk.Frame(tab4,bg="white"); chart_frame4.grid(row=2,column=0,columnspan=4,pady=10)

# ---- Tab5: Skill Gap & Training ----
tab5 = tk.Frame(notebook,bg="white")
notebook.add(tab5, text="🎓 Skill Gap & Training")
tk.Button(tab5,text="Show Skill Gap Recommendations",command=show_skill_gap,bg="#80cbc4").pack(pady=10)
skill_gap_text=tk.Text(tab5,width=90,height=6); skill_gap_text.pack(pady=5)
tk.Label(tab5,text="💬 Feedback-based Recommendations", font=("Arial",12,"bold"), bg="white").pack(pady=5)
tk.Button(tab5,text="Get Feedback Recommendations", command=feedback_recommendations,bg="#80cbc4").pack(pady=5)
feedback_text=tk.Text(tab5,width=90,height=5); feedback_text.pack(pady=5)
tk.Label(tab5,text="📈 Volunteer Engagement", font=("Arial",12,"bold"), bg="white").pack(pady=5)
volunteer_id_entry=tk.Entry(tab5,width=10); volunteer_id_entry.pack()
tk.Button(tab5,text="Check Engagement", command=volunteer_engagement,bg="#80cbc4").pack(pady=5)
engagement_label=tk.Label(tab5,text="", bg="white", font=("Arial",10)); engagement_label.pack(pady=5)
tk.Label(tab5,text="🧭 Training Suggestions", font=("Arial",12,"bold"), bg="white").pack(pady=5)
training_volunteer_id=tk.Entry(tab5,width=10); training_volunteer_id.pack()
tk.Button(tab5,text="Get Training Suggestions", command=training_suggestions,bg="#80cbc4").pack(pady=5)
training_text=tk.Text(tab5,width=90,height=5); training_text.pack(pady=10)
chart_frame5=tk.Frame(tab5,bg="white"); chart_frame5.pack(pady=10)
chart_frame5b=tk.Frame(tab5,bg="white"); chart_frame5b.pack(pady=10)

# ------------------------------
# Run App
# ------------------------------
root.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

API_URL = "http://127.0.0.1:5001"

# ------------------------------
# Helper Functions for API Calls
# ------------------------------
def find_volunteers():
    skill = skill_entry.get().strip()
    district = district_entry.get().strip()

    if not skill:
        messagebox.showwarning("⚠️ Input Required", "Please enter a skill.")
        return

    try:
        response = requests.post(f"{API_URL}/api/skilled_volunteers",
                                 json={"skill": skill, "district": district})
        data = response.json()
        result_box.delete(*result_box.get_children())

        if not data:
            messagebox.showinfo("ℹ️ No Results", "No volunteers found.")
            clear_chart(chart_frame1)
        else:
            for v in data:
                result_box.insert("", "end", values=(v['Volunteer_Name'], v['Primary_Skill'], v['District']))
            df = pd.DataFrame(data)
            plot_skill_distribution(df, chart_frame1)
    except Exception as e:
        messagebox.showerror("❌ Error", f"Failed to fetch data: {e}")

def form_team():
    skill = skill_entry_team.get().strip()
    team_size = team_size_entry.get().strip()

    if not skill:
        messagebox.showwarning("⚠️ Input Required", "Please enter a skill.")
        return

    try:
        response = requests.post(f"{API_URL}/api/form_team",
                                 json={"skill": skill, "team_size": int(team_size)})
        data = response.json()

        team_box.delete(*team_box.get_children())
        if not data:
            clear_chart(chart_frame2)
        else:
            for v in data:
                team_box.insert("", "end", values=(v['Volunteer_Name'], v['Primary_Skill'], v['District']))
            df = pd.DataFrame(data)
            plot_team_composition(df, chart_frame2)
    except Exception as e:
        messagebox.showerror("❌ Error", f"Error forming team: {e}")

def predict_showup():
    feature1 = feature1_entry.get().strip()
    feature2 = feature2_entry.get().strip()
    feature3 = feature3_entry.get().strip()

    if not (feature1 and feature2 and feature3):
        messagebox.showwarning("⚠️ Input Required", "Enter all three volunteer features.")
        return

    try:
        response = requests.post(f"{API_URL}/api/showup_prediction",
                                 json={"volunteer_features": [feature1, feature2, feature3]})
        data = response.json()
        prediction = data.get('prediction', 0)
        showup_result_label.config(text=f"✅ Prediction: {prediction}", fg="#00796b")
        plot_showup_prediction(prediction, chart_frame3)
    except Exception as e:
        messagebox.showerror("❌ Error", f"Failed to predict: {e}")

def recommend_volunteers():
    try:
        n = int(recommend_entry.get().strip() or 5)
        response = requests.post(f"{API_URL}/api/recommend_volunteers", json={"top_n": n})
        data = response.json()

        rec_box.delete(*rec_box.get_children())
        if not data:
            clear_chart(chart_frame4)
        else:
            for v in data:
                rec_box.insert("", "end", values=(v['Volunteer_Name'], v['Primary_Skill'], v['District']))
            df = pd.DataFrame(data)
            plot_recommendations(df, chart_frame4)
    except Exception as e:
        messagebox.showerror("❌ Error", f"Failed to recommend volunteers: {e}")

def show_skill_gap():
    try:
        response = requests.get(f"{API_URL}/api/skill_gap")
        data = response.json()
        skill_gap_text.delete(1.0, tk.END)
        if data:
            for skill, suggestion in data.items():
                skill_gap_text.insert(tk.END, f"🌱 {skill} → {suggestion}\n")
            df = pd.DataFrame(list(data.items()), columns=["Skill","Suggestion"])
            plot_skill_gap(df, chart_frame5)
        else:
            clear_chart(chart_frame5)
    except Exception as e:
        messagebox.showerror("❌ Error", f"Error loading skill gap info: {e}")

def feedback_recommendations():
    try:
        response = requests.post(f"{API_URL}/api/feedback_recommendations", json={})
        data = response.json()
        feedback_text.delete(1.0, tk.END)
        if data.get("recommendations"):
            for rec in data["recommendations"]:
                feedback_text.insert(tk.END, f"⭐ {rec}\n")
        else:
            feedback_text.insert(tk.END, "No recommendations available.")
    except Exception as e:
        messagebox.showerror("❌ Error", f"Failed to load feedback recommendations: {e}")

def volunteer_engagement():
    volunteer_id = volunteer_id_entry.get().strip()
    if not volunteer_id:
        messagebox.showwarning("⚠️ Input Required", "Enter a Volunteer ID.")
        return

    try:
        response = requests.get(f"{API_URL}/api/volunteer_engagement/{volunteer_id}")
        data = response.json()
        engagement_label.config(
            text=f"🕒 Hours Logged: {data['hours_logged']} | 🎯 Events Participated: {data['events_participated']}",
            fg="#004d40"
        )
        plot_engagement(data, chart_frame5b)
    except Exception as e:
        messagebox.showerror("❌ Error", f"Error fetching engagement data: {e}")

def training_suggestions():
    volunteer_id = training_volunteer_id.get().strip()
    if not volunteer_id:
        messagebox.showwarning("⚠️ Input Required", "Enter a Volunteer ID.")
        return

    try:
        response = requests.get(f"{API_URL}/api/training_suggestions/{volunteer_id}")
        data = response.json()
        training_text.delete(1.0, tk.END)
        if data.get("suggestions"):
            for s in data["suggestions"]:
                training_text.insert(tk.END, f"🎓 {s}\n")
        else:
            training_text.insert(tk.END, "No training suggestions available.")
    except Exception as e:
        messagebox.showerror("❌ Error", f"Error fetching training suggestions: {e}")

# ------------------------------
# Chart Utility Functions
# ------------------------------
def clear_chart(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def plot_skill_distribution(df, frame):
    clear_chart(frame)
    fig, ax = plt.subplots(figsize=(5,3))
    counts = df['Primary_Skill'].value_counts()
    ax.bar(counts.index, counts.values, color="#80cbc4")
    ax.set_title("Volunteers per Skill")
    ax.set_ylabel("Count")
    ax.set_xticklabels(counts.index, rotation=45, ha="right")
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def plot_team_composition(df, frame):
    clear_chart(frame)
    fig, ax = plt.subplots(figsize=(5,3))
    counts = df['Primary_Skill'].value_counts()
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90, colors=plt.cm.Pastel1.colors)
    ax.set_title("Team Skill Composition")
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def plot_showup_prediction(prediction, frame):
    clear_chart(frame)
    fig, ax = plt.subplots(figsize=(5,2))
    ax.bar(["Prediction"], [prediction], color="#80cbc4")
    ax.set_ylim(0,100)
    ax.set_ylabel("Attendance Probability (%)")
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def plot_recommendations(df, frame):
    clear_chart(frame)
    fig, ax = plt.subplots(figsize=(5,3))
    names = df['Volunteer_Name']
    ax.barh(names, range(len(names),0,-1), color="#80cbc4")
    ax.set_title("Top Recommended Volunteers")
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def plot_skill_gap(df, frame):
    clear_chart(frame)
    fig, ax = plt.subplots(figsize=(5,3))
    ax.barh(df['Skill'], range(len(df),0,-1), color="#80cbc4")
    ax.set_title("Skill Gap Analysis")
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def plot_engagement(data, frame):
    clear_chart(frame)
    fig, ax = plt.subplots(figsize=(5,3))
    ax.bar(["Hours Logged", "Events Participated"], [data['hours_logged'], data['events_participated']], color="#80cbc4")
    ax.set_title("Volunteer Engagement")
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# ------------------------------
# GUI Setup
# ------------------------------
root = tk.Tk()
root.title("🌍 SEVASETU")
root.geometry("950x800")
root.config(bg="#e8f5e9")

# Header
title = tk.Label(root, text="🤝 NGO Volunteer Management System", font=("Helvetica",20,"bold"),
                 bg="#004d40", fg="white", padx=15, pady=15)
title.pack(fill="x")

# ------------------------------
# Home Page
# ------------------------------
def show_main_app(tab_index=0):
    home_frame.pack_forget()
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    notebook.select(tab_index)

home_frame = tk.Frame(root, bg="#e0f7fa")
home_frame.pack(fill="both", expand=True)

welcome_label = tk.Label(home_frame, text="🌍 Welcome to SEVASETU",
                         font=("Helvetica",28,"bold"), bg="#e0f7fa", fg="#004d40", pady=20)
welcome_label.pack()

intro_label = tk.Label(home_frame, text="Manage volunteers, form teams, predict attendance, and track engagement—all in one place!",
                       font=("Arial",14), bg="#e0f7fa", fg="#004d40", wraplength=800, justify="center")
intro_label.pack(pady=10)

cards_frame = tk.Frame(home_frame, bg="#e0f7fa")
cards_frame.pack(pady=30)

features = [
    ("🔍 Find Volunteers", "Search volunteers by skill & district", 0),
    ("👥 Form Teams", "Auto-create teams based on skill & size", 1),
    ("📊 Show-up Prediction", "Predict volunteer attendance", 2),
    ("🌟 Recommendations", "Get top volunteers for events", 3),
    ("🌱 Skill Gap Analysis", "Identify missing skills & training", 4),
]

for i, (title_text, desc_text, tab_idx) in enumerate(features):
    card = tk.Frame(cards_frame, bg="white", bd=2, relief="raised", width=200, height=100)
    card.grid(row=i//2, column=i%2, padx=15, pady=15)
    card.pack_propagate(False)
    tk.Label(card, text=title_text, font=("Arial",12,"bold"), bg="white").pack(pady=5)
    tk.Label(card, text=desc_text, font=("Arial",10), bg="white", wraplength=180, justify="center").pack(pady=5)
    tk.Button(card, text="Go", bg="#80cbc4", fg="black", command=lambda idx=tab_idx: show_main_app(idx)).pack(pady=5)

# ------------------------------
# Notebook Tabs
# ------------------------------
notebook = ttk.Notebook(root)

# ---- Tab1: Find Volunteers ----
tab1 = tk.Frame(notebook, bg="#ffffff")
notebook.add(tab1, text="🔍 Find Volunteers")
tk.Label(tab1, text="Skill:", bg="white").grid(row=0,column=0,padx=10,pady=5,sticky="w")
skill_entry = tk.Entry(tab1,width=25); skill_entry.grid(row=0,column=1)
tk.Label(tab1, text="District:", bg="white").grid(row=0,column=2,padx=10,pady=5,sticky="w")
district_entry = tk.Entry(tab1,width=25); district_entry.grid(row=0,column=3)
tk.Button(tab1,text="Search", command=find_volunteers, bg="#80cbc4").grid(row=0,column=4,padx=10)

columns=("Volunteer_Name","Primary_Skill","District")
result_box = ttk.Treeview(tab1, columns=columns, show="headings", height=12)
for col in columns:
    result_box.heading(col,text=col)
    result_box.column(col,width=200)
result_box.grid(row=1,column=0,columnspan=5,pady=10)

chart_frame1 = tk.Frame(tab1, bg="white")
chart_frame1.grid(row=2,column=0,columnspan=5,pady=10)

# ---- Tab2: Form Team ----
tab2 = tk.Frame(notebook, bg="white")
notebook.add(tab2, text="👥 Form Team")
tk.Label(tab2, text="Skill:", bg="white").grid(row=0,column=0,padx=10,pady=5)
skill_entry_team = tk.Entry(tab2,width=25); skill_entry_team.grid(row=0,column=1)
tk.Label(tab2, text="Team Size:", bg="white").grid(row=0,column=2,padx=10,pady=5)
team_size_entry = tk.Entry(tab2,width=10); team_size_entry.insert(0,"5"); team_size_entry.grid(row=0,column=3)
tk.Button(tab2, text="Form Team", command=form_team, bg="#80cbc4").grid(row=0,column=4,padx=10)
team_box = ttk.Treeview(tab2, columns=columns, show="headings", height=12)
for col in columns:
    team_box.heading(col,text=col)
    team_box.column(col,width=200)
team_box.grid(row=1,column=0,columnspan=5,pady=10)
chart_frame2 = tk.Frame(tab2,bg="white"); chart_frame2.grid(row=2,column=0,columnspan=5,pady=10)

# ---- Tab3: Show-up Prediction ----
tab3 = tk.Frame(notebook,bg="white")
notebook.add(tab3, text="📊 Show-up Prediction")
feature_labels = ["Availability (Available/Busy)","Attendance Rate (%)","Distance from Event (km)"]
feature_entries=[]
for i,label in enumerate(feature_labels):
    tk.Label(tab3,text=label+":", bg="white").grid(row=i,column=0,padx=10,pady=5,sticky="w")
    entry=tk.Entry(tab3,width=25); entry.grid(row=i,column=1,padx=10,pady=5)
    feature_entries.append(entry)
feature1_entry, feature2_entry, feature3_entry = feature_entries
tk.Button(tab3,text="Predict", command=predict_showup,bg="#80cbc4").grid(row=3,column=0,columnspan=2,pady=10)
showup_result_label = tk.Label(tab3,text="", font=("Arial",12,"bold"), bg="white"); showup_result_label.grid(row=4,column=0,columnspan=2,pady=10)
chart_frame3 = tk.Frame(tab3,bg="white"); chart_frame3.grid(row=5,column=0,columnspan=2,pady=10)

# ---- Tab4: Recommendations ----
tab4 = tk.Frame(notebook,bg="white")
notebook.add(tab4, text="🌟 Recommendations")
tk.Label(tab4,text="Top N Volunteers:", bg="white").grid(row=0,column=0,padx=10,pady=5)
recommend_entry=tk.Entry(tab4,width=10); recommend_entry.insert(0,"5"); recommend_entry.grid(row=0,column=1)
tk.Button(tab4,text="Get Recommendations", command=recommend_volunteers,bg="#80cbc4").grid(row=0,column=2,padx=10)
rec_box = ttk.Treeview(tab4, columns=columns, show="headings", height=12)
for col in columns:
    rec_box.heading(col,text=col); rec_box.column(col,width=200)
rec_box.grid(row=1,column=0,columnspan=4,pady=10)
chart_frame4 = tk.Frame(tab4,bg="white"); chart_frame4.grid(row=2,column=0,columnspan=4,pady=10)

# ---- Tab5: Skill Gap & Training ----
tab5 = tk.Frame(notebook,bg="white")
notebook.add(tab5, text="🎓 Skill Gap & Training")
tk.Button(tab5,text="Show Skill Gap Recommendations",command=show_skill_gap,bg="#80cbc4").pack(pady=10)
skill_gap_text=tk.Text(tab5,width=90,height=6); skill_gap_text.pack(pady=5)
tk.Label(tab5,text="💬 Feedback-based Recommendations", font=("Arial",12,"bold"), bg="white").pack(pady=5)
tk.Button(tab5,text="Get Feedback Recommendations", command=feedback_recommendations,bg="#80cbc4").pack(pady=5)
feedback_text=tk.Text(tab5,width=90,height=5); feedback_text.pack(pady=5)
tk.Label(tab5,text="📈 Volunteer Engagement", font=("Arial",12,"bold"), bg="white").pack(pady=5)
volunteer_id_entry=tk.Entry(tab5,width=10); volunteer_id_entry.pack()
tk.Button(tab5,text="Check Engagement", command=volunteer_engagement,bg="#80cbc4").pack(pady=5)
engagement_label=tk.Label(tab5,text="", bg="white", font=("Arial",10)); engagement_label.pack(pady=5)
tk.Label(tab5,text="🧭 Training Suggestions", font=("Arial",12,"bold"), bg="white").pack(pady=5)
training_volunteer_id=tk.Entry(tab5,width=10); training_volunteer_id.pack()
tk.Button(tab5,text="Get Training Suggestions", command=training_suggestions,bg="#80cbc4").pack(pady=5)
training_text=tk.Text(tab5,width=90,height=5); training_text.pack(pady=10)
chart_frame5=tk.Frame(tab5,bg="white"); chart_frame5.pack(pady=10)
chart_frame5b=tk.Frame(tab5,bg="white"); chart_frame5b.pack(pady=10)

# ------------------------------
# Run App
# ------------------------------
root.mainloop()

