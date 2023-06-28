import tkinter as tk
import tkinter.messagebox as messagebox
import sqlite3
from tkinter import ttk
from ttkthemes import ThemedStyle

# Database initialization
conn = sqlite3.connect("todo_list.db")
cursor = conn.cursor()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS tasks (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       task TEXT,
       status INTEGER DEFAULT 0
    )"""
)
conn.commit()

# GUI initialization
root = tk.Tk()
root.title("To-Do List")
root.iconbitmap('./assets/icon.ico')
root.resizable(False, False)  # Set root window non-resizable

# Set the theme
style = ThemedStyle(root)
style.set_theme("clam")

# License information
license_text = open('LICENSE.md','r',encoding='utf8').read()

# Function to add a new task to the database and update the list
def add_task():
    task = entry_task.get().strip()
    if task:
        cursor.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
        conn.commit()
        list_tasks.insert(tk.END, task)
        entry_task.delete(0, tk.END)

# Function to remove a task from the database and the list
def remove_task():
    selection = list_tasks.curselection()
    if selection:
        task = list_tasks.get(selection[0])
        confirmed = messagebox.askyesno("Confirm", f"Are you sure you want to remove '{task}'?")
        if confirmed:
            cursor.execute("DELETE FROM tasks WHERE task=?", (task,))
            conn.commit()
            list_tasks.delete(selection[0])

# Function to mark a task as completed
def complete_task():
    selection = list_tasks.curselection()
    if selection:
        task = list_tasks.get(selection[0])
        status = 1 if list_tasks.itemcget(selection[0], "fg") == "gray" else 0
        new_status = 1 - status
        cursor.execute("UPDATE tasks SET status=? WHERE task=?", (new_status, task))
        conn.commit()
        if new_status == 1:
            list_tasks.itemconfig(selection[0], fg="gray")
        else:
            list_tasks.itemconfig(selection[0], fg="black")
        list_tasks.selection_clear(selection[0])

# Function to clear all tasks from the list and database
def clear_tasks():
    confirmed = messagebox.askyesno("Confirm", "Are you sure you want to clear all tasks?")
    if confirmed:
        cursor.execute("DELETE FROM tasks")
        conn.commit()
        list_tasks.delete(0, tk.END)

# Function to clear all completed tasks from the list and database
def clear_completed_tasks():
    confirmed = messagebox.askyesno("Confirm", "Are you sure you want to clear all completed tasks?")
    if confirmed:
        cursor.execute("DELETE FROM tasks WHERE status=1")
        conn.commit()
        list_tasks.delete(0, tk.END)
        cursor.execute("SELECT task, status FROM tasks")
        tasks = cursor.fetchall()
        for task, status in tasks:
            list_tasks.insert(tk.END, task)
            if status == 1:
                list_tasks.itemconfig(tk.END, fg="gray")

# Function to display the license information in a separate window
def show_license():
    license_window = tk.Toplevel(root)
    license_window.title("License")
    license_window.iconbitmap('./assets/icon.ico')
    license_window.resizable(False, False)  # Set license window non-resizable

    text_widget = tk.Text(license_window, wrap=tk.WORD, font=("Courier New", 10))
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH)

    scrollbar = ttk.Scrollbar(license_window, command=text_widget.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_widget.insert(tk.END, license_text)
    text_widget.config(yscrollcommand=scrollbar.set)
    text_widget.configure(state="disabled")

# Function to display an about dialog
def about():
    messagebox.showinfo("About", "To-Do List Application by Chanila Vidmal")

# Create and configure GUI widgets
frame_input = ttk.Frame(root)
frame_input.pack(padx=10, pady=10)

label_task = ttk.Label(frame_input, text="Task:")
label_task.grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)

entry_task = ttk.Entry(frame_input, width=40)
entry_task.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

button_add = ttk.Button(frame_input, text="Add Task", command=add_task)
button_add.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

frame_tasks = ttk.Frame(root)
frame_tasks.pack(padx=10, pady=10)

list_tasks = tk.Listbox(frame_tasks, width=50, height=10, font=("Arial", 12))
list_tasks.pack(side=tk.LEFT, fill=tk.BOTH)

# Scrollbar for the task list
scrollbar = ttk.Scrollbar(frame_tasks, orient=tk.VERTICAL, command=list_tasks.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

list_tasks.config(yscrollcommand=scrollbar.set)
list_tasks.configure(yscrollcommand=scrollbar.set)

# Populate the list with tasks from the database
cursor.execute("SELECT task, status FROM tasks")
tasks = cursor.fetchall()
for task, status in tasks:
    list_tasks.insert(tk.END, task)
    if status == 1:
        list_tasks.itemconfig(tk.END, fg="gray")

# Menu bar
menubar = tk.Menu(root)
root.config(menu=menubar)

file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Clear All Tasks", command=clear_tasks)
file_menu.add_command(label="Clear Completed Tasks", command=clear_completed_tasks)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

help_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About", command=about)
help_menu.add_separator()
help_menu.add_command(label="License", command=show_license)
help_menu.add_command(label="Keyboard Shortcuts",
                      command=lambda: messagebox.showinfo("Keyboard Shortcuts",
                                                          "Add Task: Enter\n"
                                                          "Remove Task: Delete\n"
                                                          "Mark as Completed: Space"))

# Keyboard shortcuts
root.bind("<Return>", lambda event: add_task())
root.bind("<Delete>", lambda event: remove_task())
root.bind("<space>", lambda event: complete_task())

# Context menu for the task list
context_menu = tk.Menu(root, tearoff=0)

def popup(event):
    selection = list_tasks.curselection()
    if selection:
        context_menu.tk_popup(event.x_root, event.y_root)

context_menu.add_command(label="Remove Task", command=remove_task)
context_menu.add_command(label="Mark as Completed", command=complete_task)

list_tasks.bind("<Button-3>", popup)

# Run the GUI
root.mainloop()

# Close the database connection
conn.close()
