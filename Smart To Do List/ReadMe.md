
# SMART TO-DO LIST – PROJECT REPORT

---

## Output Screenshot (Description)

<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/8e080abc-a2f6-4c60-9dc0-26eda0751fec" />


A clean window appears with:

* Task input box
* Add button
* List of tasks
* Buttons for Edit, Delete, Complete
* Simple light-grey background

---

## Introduction

The Smart To-Do List is a simple productivity application developed using **Python Tkinter**.
It allows users to add, edit, delete, and manage daily tasks in an organized way.
This project demonstrates basic GUI development, event handling, and file handling in Python.

---

##  Objective

* To create a clean and user-friendly GUI application
* To help users manage tasks efficiently
* To demonstrate Tkinter widgets such as Buttons, Entry, Listbox, Scrollbar
* To practice real-time functionality such as saving and loading tasks

---

## ** Technologies Used**

* **Python 3**
* **Tkinter** (for GUI)
* **JSON** (for data storage)

---


## ** System Requirements**

* Windows / Mac / Linux
* Python 3 installed
* Tkinter (comes pre-installed)
* 
---
### **Creating the Main Window**

```python
root = Tk()
root.title("Smart To-Do List")
root.geometry("400x500")
root.configure(bg="#F5F5F5")
```

### **Adding Tasks**

```python
def add_task():
    task = entry_task.get()
    if task:
        listbox_tasks.insert(END, task)
        entry_task.delete(0, END)
        save_tasks()
```

### **Marking Tasks Completed**

```python
def mark_completed():
    selected = listbox_tasks.curselection()
    if selected:
        index = selected[0]
        task = listbox_tasks.get(index)
        listbox_tasks.delete(index)
        listbox_tasks.insert(index, "✔ " + task)
        save_tasks()
```

### **Saving Tasks**

```python
def save_tasks():
    tasks = list(listbox_tasks.get(0, END))
    with open("tasks.json", "w") as f:
        json.dump(tasks, f)
```



---

## ** Conclusion**

The Smart To-Do List project is a simple yet effective Tkinter application.
It demonstrates core concepts of GUI design, user interaction, and data storage.
This project can be expanded with features like notifications, dark mode, or calendar integration.

---

