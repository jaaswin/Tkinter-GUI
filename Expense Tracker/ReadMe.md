# 📒 Expense Tracker – Python Tkinter

A simple and user-friendly **Expense Tracker GUI application** built using **Python Tkinter**.
This app allows you to enter daily expenses, categorize them, store them in a CSV file, and view them instantly in a table.

---

## 🖼️ Screenshot

<img width="602" height="532" alt="image" src="https://github.com/user-attachments/assets/ce6f8188-0258-40c0-9d92-c0127b185ccf" />

---

## ✨ Features

✔ Add expenses with category, amount & note
✔ Auto-save and load from CSV
✔ Displays data in a table (Treeview)
✔ Lightweight – no database needed
✔ Beginner-friendly Tkinter code
✔ Works on Windows, Mac & Linux



---

## 🚀 How to Run

### 1️⃣ Install Python

Download from: [https://www.python.org/](https://www.python.org/)

### 2️⃣ Run the script

```bash
python expense_tracker.py
```

No external libraries required 🎉

---

## 📌 Code Highlight (Main Logic)

```python
with open("expenses.csv", "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([date, category, amount, note])
```

---

## 📊 Future Enhancements

🔹 Monthly summary
🔹 Pie chart visualization
🔹 Filter/search expenses
🔹 Export to PDF/Excel
🔹 SQLite version
🔹 GUI theme upgrade

---


## 🙌 Contributions

Pull requests are welcome!
Feel free to **fork** this project and improve it.

---

## ⭐ Support

If you like this project, don't forget to ⭐ **star the repo**!

---


