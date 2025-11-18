import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime

FILE = "expenses.csv"

# -----------------------------
# Save Expense to CSV
# -----------------------------
def save_expense():
    category = category_var.get()
    amount = amount_var.get()
    note = note_var.get()
    
    if not amount.isdigit():
        messagebox.showerror("Invalid Input", "Amount must be a number!")
        return
    
    if category == "":
        messagebox.showerror("Error", "Select a category!")
        return

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to CSV
    file_exists = os.path.isfile(FILE)
    with open(FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Date", "Category", "Amount", "Note"])
        writer.writerow([date, category, amount, note])
    
    messagebox.showinfo("Saved", "Expense added successfully!")
    amount_var.set("")
    note_var.set("")
    load_table()

# -----------------------------
# Load data from CSV to table
# -----------------------------
def load_table():
    for row in expense_table.get_children():
        expense_table.delete(row)

    if os.path.exists(FILE):
        with open(FILE) as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                expense_table.insert("", tk.END, values=row)

# -----------------------------
# UI Setup
# -----------------------------
window = tk.Tk()
window.title("Expense Tracker")
window.geometry("600x500")
window.configure(bg="#1e1e1e")

title = tk.Label(window, text="Expense Tracker", font=("Arial", 20, "bold"), bg="#1e1e1e", fg="white")
title.pack(pady=10)

frame = ttk.Frame(window)
frame.pack(pady=5)

# User Input Fields
ttk.Label(frame, text="Category:").grid(row=0, column=0, padx=5, pady=5)
category_var = tk.StringVar()
category_dropdown = ttk.Combobox(frame, textvariable=category_var, state="readonly", width=20)
category_dropdown["values"] = ["Food", "Transport", "Shopping", "Bills", "Others"]
category_dropdown.grid(row=0, column=1)

ttk.Label(frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5)
amount_var = tk.StringVar()
amount_entry = ttk.Entry(frame, textvariable=amount_var)
amount_entry.grid(row=1, column=1)

ttk.Label(frame, text="Note:").grid(row=2, column=0, padx=5, pady=5)
note_var = tk.StringVar()
note_entry = ttk.Entry(frame, textvariable=note_var, width=25)
note_entry.grid(row=2, column=1)

# Button
ttk.Button(frame, text="Add Expense", command=save_expense).grid(row=3, column=0, columnspan=2, pady=10)

# Table
columns = ["Date", "Category", "Amount", "Note"]
expense_table = ttk.Treeview(window, columns=columns, show="headings")

for col in columns:
    expense_table.heading(col, text=col)
    expense_table.column(col, width=130)

expense_table.pack(pady=10, fill="both", expand=True)

load_table()
window.mainloop()
