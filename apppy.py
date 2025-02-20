import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from PIL import Image, ImageTk
import customtkinter as ctk
import sqlite3
import os
import platform

# SQLite Database Setup
def create_database():
    conn = sqlite3.connect('ido.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  category TEXT,
                  campus TEXT,
                  building TEXT,
                  project_title TEXT,
                  date_started TEXT,
                  date_finished TEXT,
                  contractor TEXT,
                  file_path TEXT)''')
    conn.commit()
    conn.close()

def fetch_records(search_query=None):
    conn = sqlite3.connect('ido.db')
    c = conn.cursor()
    if search_query:
        c.execute("SELECT * FROM projects WHERE category LIKE ? OR campus LIKE ? OR building LIKE ? OR contractor LIKE ? OR project_title LIKE ?",
                  (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
    else:
        c.execute("SELECT * FROM projects")
    records = c.fetchall()
    conn.close()
    return records

def insert_record(record):
    conn = sqlite3.connect('ido.db')
    c = conn.cursor()
    c.execute("INSERT INTO projects (category, campus, building, project_title, date_started, date_finished, contractor, file_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              record)
    conn.commit()
    conn.close()

def update_record(record_id, record):
    conn = sqlite3.connect('ido.db')
    c = conn.cursor()
    c.execute("UPDATE projects SET category=?, campus=?, building=?, project_title=?, date_started=?, date_finished=?, contractor=?, file_path=? WHERE id=?",
              (*record, record_id))
    conn.commit()
    conn.close()

def delete_record_db(record_id):
    conn = sqlite3.connect('ido.db')
    c = conn.cursor()
    c.execute("DELETE FROM projects WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

# Function to open file path
def open_file_path(file_path):
    if os.path.exists(file_path):
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":  # macOS
            os.system(f"open {file_path}")
        else:  # Linux
            os.system(f"xdg-open {file_path}")
    else:
        messagebox.showwarning("File Not Found", f"The file or directory does not exist:\n{file_path}")

# GUI Functions
def validate_login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "admin" and password == "ido":
        login_frame.pack_forget()
        main_frame.pack(fill=tk.BOTH, expand=True)
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        load_table()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

def load_table():
    for row in table.get_children():
        table.delete(row)
    records = fetch_records()
    for record in records:
        formatted_id = f"{record[0]:04d}"
        table.insert("", "end", values=(formatted_id, *record[1:]))

def perform_search():
    search_query = search_entry.get()
    for row in table.get_children():
        table.delete(row)
    records = fetch_records(search_query)
    for record in records:
        formatted_id = f"{record[0]:04d}"
        table.insert("", "end", values=(formatted_id, *record[1:]))

def log_out():
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    main_frame.pack_forget()
    login_frame.pack(fill=tk.BOTH, expand=True)

def on_restore(event):
    root.geometry("800x600")

def toggle_password_visibility():
    if password_entry.cget("show") == "*":
        password_entry.configure(show="")
        toggle_button.configure(image=hide_icon_tk)
    else:
        password_entry.configure(show="*")
        toggle_button.configure(image=show_icon_tk)

def delete_record():
    selected_item = table.selection()
    if selected_item:
        confirm = messagebox.askyesno("Delete Record", "Are you sure you want to delete this record?")
        if confirm:
            record_id = table.item(selected_item, "values")[0]
            delete_record_db(int(record_id))
            table.delete(selected_item)
    else:
        messagebox.showwarning("No Selection", "Please select a record to delete.")

def edit_record():
    selected_item = table.selection()
    if selected_item:
        current_values = table.item(selected_item, "values")
        open_edit_add_window(current_values, selected_item)
    else:
        messagebox.showwarning("No Selection", "Please select a record to edit.")

def add_record():
    open_edit_add_window()

def open_edit_add_window(current_values=None, selected_item=None):
    edit_add_window = tk.Toplevel(root)
    edit_add_window.title("Edit/Add Record" if current_values else "Add Record")
    edit_add_window.geometry("500x500")
    edit_add_window.configure(bg="#e5ecff")

    categories = ["IP", "SVP"]
    campuses = ["Atate", "Carranglan", "Fort Magsaysay", "Gabaldon", "General Tinio St.","Nampicuan", "Papaya", "Penaranda", "San Antonio", "San Isidro", "San Leonardo", "Sto. Domingo", "Sumacab", "Talavera" ]
    buildings = ["Admin", "CICT", "COED", "CMBT", "CEn", "Arki", "COC", "Others"]

    tk.Label(edit_add_window, text="Category:", bg="#e5ecff").grid(row=0, column=0, padx=10, pady=10)
    category_var = tk.StringVar(value=current_values[1] if current_values else categories[0])
    category_dropdown = ttk.Combobox(edit_add_window, textvariable=category_var, values=categories, state="readonly")
    category_dropdown.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(edit_add_window, text="Campus:", bg="#e5ecff").grid(row=1, column=0, padx=10, pady=10)
    campus_var = tk.StringVar(value=current_values[2] if current_values else campuses[0])
    campus_dropdown = ttk.Combobox(edit_add_window, textvariable=campus_var, values=campuses, state="readonly")
    campus_dropdown.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(edit_add_window, text="Building:", bg="#e5ecff").grid(row=2, column=0, padx=10, pady=10)
    building_var = tk.StringVar(value=current_values[3] if current_values else buildings[0])
    building_dropdown = ttk.Combobox(edit_add_window, textvariable=building_var, values=buildings, state="readonly")
    building_dropdown.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(edit_add_window, text="Project Title:", bg="#e5ecff").grid(row=3, column=0, padx=10, pady=10)
    project_title_entry = ctk.CTkEntry(edit_add_window, font=("Helvetica", 12), width=200, height=30, corner_radius=10, fg_color="#ffffff", border_color="#0078d7", text_color="#000000")
    project_title_entry.insert(0, current_values[4] if current_values else "")
    project_title_entry.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(edit_add_window, text="Date Started:", bg="#e5ecff").grid(row=4, column=0, padx=10, pady=10)
    date_started_entry = ctk.CTkEntry(edit_add_window, font=("Helvetica", 12), width=200, height=30, corner_radius=10, fg_color="#ffffff", border_color="#0078d7", text_color="#000000")
    date_started_entry.insert(0, current_values[5] if current_values else "")
    date_started_entry.grid(row=4, column=1, padx=10, pady=10)

    tk.Label(edit_add_window, text="Date Finished:", bg="#e5ecff").grid(row=5, column=0, padx=10, pady=10)
    date_finished_entry = ctk.CTkEntry(edit_add_window, font=("Helvetica", 12), width=200, height=30, corner_radius=10, fg_color="#ffffff", border_color="#0078d7", text_color="#000000")
    date_finished_entry.insert(0, current_values[6] if current_values else "")
    date_finished_entry.grid(row=5, column=1, padx=10, pady=10)

    tk.Label(edit_add_window, text="Contractor:", bg="#e5ecff").grid(row=6, column=0, padx=10, pady=10)
    contractor_entry = ctk.CTkEntry(edit_add_window, font=("Helvetica", 12), width=200, height=30, corner_radius=10, fg_color="#ffffff", border_color="#0078d7", text_color="#000000")
    contractor_entry.insert(0, current_values[7] if current_values else "")
    contractor_entry.grid(row=6, column=1, padx=10, pady=10)

    tk.Label(edit_add_window, text="File Path/Directory:", bg="#e5ecff").grid(row=7, column=0, padx=10, pady=10)
    file_path_entry = ctk.CTkEntry(edit_add_window, font=("Helvetica", 12), width=350, height=30, corner_radius=10, fg_color="#ffffff", border_color="#0078d7", text_color="#000000")
    file_path_entry.insert(0, current_values[8] if current_values else "")
    file_path_entry.grid(row=7, column=1, padx=10, pady=10)

    def save_record():
        new_values = [
            category_var.get(),
            campus_var.get(),
            building_var.get(),
            project_title_entry.get(),
            date_started_entry.get(),
            date_finished_entry.get(),
            contractor_entry.get(),
            file_path_entry.get()
        ]
        if current_values:
            record_id = int(current_values[0])
            update_record(record_id, new_values)
        else:
            insert_record(new_values)
        load_table()
        edit_add_window.destroy()

    save_button = ctk.CTkButton(edit_add_window, text="Save", command=save_record, font=("Helvetica", 12), fg_color="#0078d7", hover_color="#004a99", corner_radius=20)
    save_button.grid(row=8, column=0, columnspan=2, pady=10)

# Function to sort the table
def sort_table(col, reverse):
    data = [(table.set(child, col), child) for child in table.get_children('')]
    data.sort(reverse=reverse)
    for index, (val, child) in enumerate(data):
        table.move(child, '', index)
    table.heading(col, command=lambda: sort_table(col, not reverse))

# Create the main application window
root = tk.Tk()
root.title("Infrastructure Development Office")
root.geometry("800x600")
root.configure(bg="#e5ecff")

# Maximize the window on startup
root.state('zoomed')

root.bind("<Unmap>", on_restore)

login_frame = tk.Frame(root, bg="#e5ecff")
main_frame = tk.Frame(root, bg="#e5ecff")

try:
    login_logo_image = Image.open("C:/Users/joshua/Documents/pyapp/neustlogo.png")
    login_logo_image = login_logo_image.resize((150, 150), Image.Resampling.LANCZOS)
    login_logo_image_tk = ImageTk.PhotoImage(login_logo_image)

    home_logo_image = Image.open("C:/Users/joshua/Documents/pyapp/neustlogo.png")
    home_logo_image = home_logo_image.resize((70, 70), Image.Resampling.LANCZOS)
    home_logo_image_tk = ImageTk.PhotoImage(home_logo_image)

    username_icon = Image.open("C:/Users/joshua/Documents/pyapp/user.png")
    username_icon = username_icon.resize((25, 25), Image.Resampling.LANCZOS)
    username_icon_tk = ImageTk.PhotoImage(username_icon)

    password_icon = Image.open("C:/Users/joshua/Documents/pyapp/lock.png")
    password_icon = password_icon.resize((25, 25), Image.Resampling.LANCZOS)
    password_icon_tk = ImageTk.PhotoImage(password_icon)

    logout_icon = Image.open("C:/Users/joshua/Documents/pyapp/logout.png")
    logout_icon = logout_icon.resize((25, 25), Image.Resampling.LANCZOS)
    logout_icon_tk = ImageTk.PhotoImage(logout_icon)

    search_icon = Image.open("C:/Users/joshua/Documents/pyapp/search.png")
    search_icon = search_icon.resize((20, 20), Image.Resampling.LANCZOS)
    search_icon_tk = ImageTk.PhotoImage(search_icon)

    show_icon = Image.open("C:/Users/joshua/Documents/pyapp/show.png")
    show_icon = show_icon.resize((20, 20), Image.Resampling.LANCZOS)
    show_icon_tk = ImageTk.PhotoImage(show_icon)

    hide_icon = Image.open("C:/Users/joshua/Documents/pyapp/hide.png")
    hide_icon = hide_icon.resize((20, 20), Image.Resampling.LANCZOS)
    hide_icon_tk = ImageTk.PhotoImage(hide_icon)

    delete_icon = Image.open("C:/Users/joshua/Documents/pyapp/trash.png")
    delete_icon = delete_icon.resize((20, 20), Image.Resampling.LANCZOS)
    delete_icon_tk = ImageTk.PhotoImage(delete_icon)

    edit_icon = Image.open("C:/Users/joshua/Documents/pyapp/edit.png")
    edit_icon = edit_icon.resize((20, 20), Image.Resampling.LANCZOS)
    edit_icon_tk = ImageTk.PhotoImage(edit_icon)

    add_icon = Image.open("C:/Users/joshua/Documents/pyapp/add.png")
    add_icon = add_icon.resize((20, 20), Image.Resampling.LANCZOS)
    add_icon_tk = ImageTk.PhotoImage(add_icon)
except Exception as e:
    messagebox.showerror("Error", f"Failed to load icons: {e}")
    root.destroy()

# Login
logo_label = tk.Label(login_frame, image=login_logo_image_tk, bg="#e5ecff")
logo_label.pack(pady=(20, 10))

login_label = tk.Label(login_frame, text="Infrastructure Development Office", font=("Helvetica", 30, "bold"), bg="#e5ecff", fg="#333333")
login_label.pack(pady=(0, 20))

# Username Section
username_frame = tk.Frame(login_frame, bg="#e5ecff")
username_frame.pack(pady=10)

username_icon_label = tk.Label(username_frame, image=username_icon_tk, bg="#e5ecff")
username_icon_label.pack(side=tk.LEFT, padx=(0, 10))

username_entry = ctk.CTkEntry(username_frame, font=("Helvetica", 12), width=250, height=50, corner_radius=10, placeholder_text="Username", fg_color="#ffffff", border_color="#0078d7", text_color="#000000")
username_entry.pack(side=tk.LEFT)

# Password Section
password_frame = tk.Frame(login_frame, bg="#e5ecff")
password_frame.pack(pady=10)

password_icon_label = tk.Label(password_frame, image=password_icon_tk, bg="#e5ecff")
password_icon_label.pack(side=tk.LEFT, padx=(0, 10))

password_entry_frame = ctk.CTkFrame(password_frame, width=200, height=40, corner_radius=10, fg_color="#ffffff", border_color="#0078d7", border_width=2)
password_entry_frame.pack(side=tk.LEFT)

password_entry = ctk.CTkEntry(password_entry_frame, font=("Helvetica", 12), width=200, height=40, corner_radius=10, placeholder_text="Password", show="*", fg_color="#ffffff", text_color="#000000", border_width=0)
password_entry.pack(side=tk.LEFT, padx=(5, 0), pady=5)

toggle_button = ctk.CTkButton(password_entry_frame, text="", image=show_icon_tk, width=30, height=30, fg_color="#ffffff", hover_color="#e5ecff", command=toggle_password_visibility)
toggle_button.pack(side=tk.LEFT, padx=(0, 5), pady=5)

username_entry.bind("<Return>", lambda event: validate_login())
password_entry.bind("<Return>", lambda event: validate_login())

login_button = ctk.CTkButton(login_frame, text="Login", command=validate_login, font=("Helvetica", 15, "bold"), fg_color=("#0078d7"), hover_color=("#004a99"), corner_radius=20)
login_button.pack(pady=20)

# Main Page
top_panel = tk.Frame(main_frame, bg="#0078d7", height=100)
top_panel.pack(fill=tk.X)

logo_title_frame = tk.Frame(top_panel, bg="#0078d7")
logo_title_frame.pack(pady=30)

home_logo_label = tk.Label(logo_title_frame, image=home_logo_image_tk, bg="#0078d7")
home_logo_label.pack(side=tk.LEFT, padx=(10, 20))

title_label = tk.Label(logo_title_frame, text="Infrastructure Development Office", font=("Times New Roman", 25, "bold"), bg="#0078d7", fg="#1a1a1a")
title_label.pack(side=tk.LEFT)

# Search Field
search_frame = tk.Frame(main_frame, bg="#e5ecff")
search_frame.pack(pady=20)

search_entry = ctk.CTkEntry(search_frame, font=("Helvetica", 12), width=500, height=40, corner_radius=20, placeholder_text="Search...", fg_color="#ffffff", border_color="#0078d7", text_color="#000000")
search_entry.pack(side=tk.LEFT, padx=(80, 10))

search_entry.bind("<Return>", lambda event: perform_search())

search_button = ctk.CTkButton(search_frame, text="", image=search_icon_tk, width=40, height=40, fg_color="#ccdaff", hover_color="#99b4ff", corner_radius=20, command=perform_search)
search_button.pack(side=tk.LEFT)

# Table Frame
table_frame = tk.Frame(main_frame, bg="#e5ecff")
table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

columns = ("ID", "Category", "Campus", "Building", "Project Title", "Date Started", "Date Finished", "Contractor", "File Path/Directory")
table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

for col in columns:
    table.heading(col, text=col, command=lambda c=col: sort_table(c, False))
    table.column(col, width=120, anchor=tk.CENTER)

scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table.yview)
table.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

table.pack(fill=tk.BOTH, expand=True)

def on_triple_click(event):
    selected_item = table.selection()
    if selected_item:
        file_path = table.item(selected_item, "values")[8]
        if file_path:
            open_file_path(file_path)

table.bind("<Triple-1>", on_triple_click)

button_frame = tk.Frame(main_frame, bg="#e5ecff")
button_frame.pack(pady=10)

# Add Button
add_button = ctk.CTkButton(button_frame, text="", image=add_icon_tk, width=40, height=40, fg_color="#e5ecff", hover_color="#b3c7ff", corner_radius=20, command=add_record)
add_button.pack(side=tk.LEFT, padx=10)
# Edit Button
edit_button = ctk.CTkButton(button_frame, text="", image=edit_icon_tk, width=40, height=40, fg_color="#e5ecff", hover_color="#b3c7ff", corner_radius=20, command=edit_record)
edit_button.pack(side=tk.LEFT, padx=10)
# Delete Button
delete_button = ctk.CTkButton(button_frame, text="", image=delete_icon_tk, width=40, height=40, fg_color="#e5ecff", hover_color="#b3c7ff", corner_radius=20, command=delete_record)
delete_button.pack(side=tk.LEFT, padx=10)

# Log Out Button
log_out_button = ctk.CTkButton(main_frame, text="", command=log_out, image=logout_icon_tk, width=40, height=40, bg_color="#0078d7", fg_color="#0078d7", hover_color="#004a99", corner_radius=10)
log_out_button.place(relx=0.95, rely=0.05, anchor=tk.NE)

login_frame.pack(fill=tk.BOTH, expand=True)

# Garbage Collection Prevention
root.login_logo_image_tk = login_logo_image_tk
root.home_logo_image_tk = home_logo_image_tk
root.username_icon_tk = username_icon_tk
root.password_icon_tk = password_icon_tk
root.logout_icon_tk = logout_icon_tk
root.search_icon_tk = search_icon_tk
root.show_icon_tk = show_icon_tk
root.hide_icon_tk = hide_icon_tk
root.delete_icon_tk = delete_icon_tk
root.edit_icon_tk = edit_icon_tk
root.add_icon_tk = add_icon_tk 

create_database()

root.mainloop()