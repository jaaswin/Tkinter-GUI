#!/usr/bin/env python3
"""
smart_todo.py
Smart To-Do List with Reminders and Notifications
Single-file Tkinter app. Data saved in tasks.json

Features:
- Add / edit / delete tasks
- Priority (Low/Medium/High), Deadline (YYYY-MM-DD HH:MM), Notes
- Mark complete / incomplete
- Search & filter
- Color-coded Treeview rows via tags
- Background reminder checker (uses plyer.notification if available, otherwise Tk popup)
- Export tasks to CSV
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time
import csv
import sys

# Try system notifications via plyer (optional)
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except Exception:
    PLYER_AVAILABLE = False

DATA_FILE = Path("tasks.json")
REMINDER_CHECK_INTERVAL = 30  # seconds
REMINDER_LOOKAHEAD = 1  # minutes to pop reminder for tasks due within this window

# ---------------------------
# Task storage / management
# ---------------------------
class TaskManager:
    def __init__(self, path=DATA_FILE):
        self.path = Path(path)
        self.tasks = []  # list of dicts
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
            except Exception:
                # if corrupt, back up and start fresh
                bak = self.path.with_suffix(".bak.json")
                try:
                    self.path.rename(bak)
                except Exception:
                    pass
                self.tasks = []
        else:
            self.tasks = []

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)

    def add_task(self, title, deadline=None, priority="Medium", notes=""):
        task = {
            "id": int(time.time() * 1000),  # simple unique id
            "title": title,
            "deadline": deadline,  # string like "2025-11-25 14:30" or None
            "priority": priority,
            "notes": notes,
            "completed": False,
            "reminded": False  # whether reminder already showed
        }
        self.tasks.append(task)
        self.save()
        return task

    def update_task(self, task_id, **fields):
        for t in self.tasks:
            if t["id"] == task_id:
                t.update(fields)
                self.save()
                return t
        raise KeyError("Task not found")

    def delete_task(self, task_id):
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        if len(self.tasks) != before:
            self.save()

    def get_all(self):
        return list(self.tasks)

    def find(self, query=None):
        if not query:
            return self.get_all()
        q = query.lower()
        return [t for t in self.tasks if q in t["title"].lower() or q in (t.get("notes","").lower())]

    def mark_complete(self, task_id, completed=True):
        return self.update_task(task_id, completed=completed)

# ---------------------------
# Notification helper
# ---------------------------
def notify(title, message):
    if PLYER_AVAILABLE:
        try:
            notification.notify(title=title, message=message, timeout=8)
            return
        except Exception:
            pass
    # fallback: simple Tk popup
    try:
        # create a small transient window
        popup = tk.Toplevel()
        popup.title(title)
        popup.geometry("+%d+%d" % (popup.winfo_screenwidth() - 300, 50))
        popup.attributes("-topmost", True)
        ttk.Label(popup, text=message, wraplength=280).pack(padx=12, pady=8)
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=(0,8))
        # auto-destroy after 10s
        popup.after(10000, popup.destroy)
    except Exception:
        # final fallback: messagebox (may steal focus)
        try:
            messagebox.showinfo(title, message)
        except Exception:
            print(f"[NOTIFY] {title}: {message}", file=sys.stderr)

# ---------------------------
# Tkinter UI
# ---------------------------
class SmartToDoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart To-Do List")
        self.geometry("900x560")
        self.minsize(700, 450)
        self.style = ttk.Style(self)
        # Use default theme; user can customize later
        self.task_manager = TaskManager()
        self._build_ui()
        self._load_tasks_into_view()
        self._start_reminder_thread()

    def _build_ui(self):
        # Top frame: controls
        top = ttk.Frame(self, padding=(10,8))
        top.pack(side="top", fill="x")

        # Add Task button
        add_btn = ttk.Button(top, text="＋ Add Task", command=self._on_add_task)
        add_btn.pack(side="left")

        edit_btn = ttk.Button(top, text="✎ Edit Task", command=self._on_edit_task)
        edit_btn.pack(side="left", padx=(8,0))

        del_btn = ttk.Button(top, text="🗑 Delete Task", command=self._on_delete_task)
        del_btn.pack(side="left", padx=(8,0))

        complete_btn = ttk.Button(top, text="✓ Toggle Complete", command=self._on_toggle_complete)
        complete_btn.pack(side="left", padx=(8,0))

        export_btn = ttk.Button(top, text="Export CSV", command=self._on_export_csv)
        export_btn.pack(side="left", padx=(8,0))

        # Search
        search_label = ttk.Label(top, text="Search:")
        search_label.pack(side="left", padx=(20,4))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top, textvariable=self.search_var)
        search_entry.pack(side="left")
        search_entry.bind("<Return>", lambda e: self._on_search())
        ttk.Button(top, text="Go", command=self._on_search).pack(side="left", padx=(6,0))
        ttk.Button(top, text="Clear", command=self._on_clear_search).pack(side="left", padx=(6,0))

        # Center: Treeview
        container = ttk.Frame(self, padding=(10,8))
        container.pack(fill="both", expand=True)

        columns = ("title", "deadline", "priority", "status")
        self.tree = ttk.Treeview(container, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("title", text="Title", command=lambda: self._sort_by("title"))
        self.tree.heading("deadline", text="Deadline", command=lambda: self._sort_by("deadline"))
        self.tree.heading("priority", text="Priority", command=lambda: self._sort_by("priority"))
        self.tree.heading("status", text="Status", command=lambda: self._sort_by("completed"))

        self.tree.column("title", width=420, anchor="w")
        self.tree.column("deadline", width=160, anchor="center")
        self.tree.column("priority", width=100, anchor="center")
        self.tree.column("status", width=80, anchor="center")

        vsb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, side="left")

        # Treeview tags for colors
        self.tree.tag_configure("high", background="#ffecec")
        self.tree.tag_configure("medium", background="#fff7e6")
        self.tree.tag_configure("low", background="#ecffe8")
        self.tree.tag_configure("completed", foreground="#8a8a8a")

        # Bottom: details area
        bottom = ttk.Frame(self, padding=(10,8))
        bottom.pack(side="bottom", fill="x")
        self.details_label = ttk.Label(bottom, text="Select a task to view details.", anchor="w")
        self.details_label.pack(fill="x")

        self.tree.bind("<<TreeviewSelect>>", lambda e: self._show_selected_details())

    # ---------------------------
    # Task view population
    # ---------------------------
    def _load_tasks_into_view(self, tasks=None):
        for r in self.tree.get_children():
            self.tree.delete(r)
        tasks = tasks if tasks is not None else self.task_manager.get_all()
        # sort: uncompleted first, then by deadline (None at end)
        def sort_key(t):
            d = t.get("deadline")
            try:
                dt = datetime.strptime(d, "%Y-%m-%d %H:%M") if d else None
            except Exception:
                dt = None
            return (t.get("completed", False), dt or datetime.max, {"High":0,"Medium":1,"Low":2}.get(t.get("priority","Medium"),1))
        tasks_sorted = sorted(tasks, key=sort_key)
        for t in tasks_sorted:
            status = "Done" if t.get("completed") else "Pending"
            deadline = t.get("deadline") or ""
            tag = t.get("priority","Medium").lower()
            if t.get("completed"):
                tags = (tag, "completed")
            else:
                tags = (tag,)
            self.tree.insert("", "end", iid=str(t["id"]), values=(t["title"], deadline, t["priority"], status), tags=tags)

    # ---------------------------
    # Actions
    # ---------------------------
    def _on_add_task(self):
        dlg = TaskDialog(self, "Add Task")
        self.wait_window(dlg)
        if dlg.result:
            title, deadline, priority, notes = dlg.result
            try:
                if deadline:
                    # validate format
                    _ = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
                self.task_manager.add_task(title=title, deadline=deadline, priority=priority, notes=notes)
                self._load_tasks_into_view()
            except ValueError:
                messagebox.showerror("Invalid date", "Deadline must be in format YYYY-MM-DD HH:MM")

    def _on_edit_task(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Edit Task", "Please select a task to edit.")
            return
        task_id = int(sel[0])
        t = next((x for x in self.task_manager.get_all() if x["id"] == task_id), None)
        if not t:
            messagebox.showerror("Error", "Task not found.")
            return
        dlg = TaskDialog(self, "Edit Task", prefill=t)
        self.wait_window(dlg)
        if dlg.result:
            title, deadline, priority, notes = dlg.result
            try:
                if deadline:
                    _ = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
                self.task_manager.update_task(task_id, title=title, deadline=deadline, priority=priority, notes=notes)
                self._load_tasks_into_view()
            except ValueError:
                messagebox.showerror("Invalid date", "Deadline must be in format YYYY-MM-DD HH:MM")

    def _on_delete_task(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Delete Task", "Please select a task to delete.")
            return
        task_id = int(sel[0])
        if messagebox.askyesno("Delete Task", "Are you sure you want to delete the selected task?"):
            self.task_manager.delete_task(task_id)
            self._load_tasks_into_view()
            self.details_label.config(text="Task deleted.")

    def _on_toggle_complete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Toggle Complete", "Please select a task.")
            return
        task_id = int(sel[0])
        t = next((x for x in self.task_manager.get_all() if x["id"] == task_id), None)
        if t:
            new_state = not t.get("completed", False)
            self.task_manager.mark_complete(task_id, completed=new_state)
            self._load_tasks_into_view()

    def _on_search(self):
        q = self.search_var.get().strip()
        results = self.task_manager.find(q)
        self._load_tasks_into_view(results)

    def _on_clear_search(self):
        self.search_var.set("")
        self._load_tasks_into_view()

    def _on_export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv"),("All files","*.*")])
        if not path:
            return
        tasks = self.task_manager.get_all()
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id","title","deadline","priority","completed","notes"])
                for t in tasks:
                    writer.writerow([t.get("id"), t.get("title"), t.get("deadline"), t.get("priority"), t.get("completed"), t.get("notes","")])
            messagebox.showinfo("Export CSV", f"Exported {len(tasks)} tasks to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV:\n{e}")

    # ---------------------------
    # Sorting helper
    # ---------------------------
    def _sort_by(self, field):
        tasks = self.task_manager.get_all()
        reverse = False
        if field == "title":
            tasks = sorted(tasks, key=lambda x: x.get("title","").lower(), reverse=reverse)
        elif field == "deadline":
            def keyfn(x):
                d = x.get("deadline")
                try:
                    return datetime.strptime(d, "%Y-%m-%d %H:%M") if d else datetime.max
                except Exception:
                    return datetime.max
            tasks = sorted(tasks, key=keyfn, reverse=reverse)
        elif field == "priority":
            rank = {"High":0,"Medium":1,"Low":2}
            tasks = sorted(tasks, key=lambda x: rank.get(x.get("priority","Medium"),1), reverse=reverse)
        elif field == "completed":
            tasks = sorted(tasks, key=lambda x: x.get("completed", False), reverse=reverse)
        self._load_tasks_into_view(tasks)

    # ---------------------------
    # Details
    # ---------------------------
    def _show_selected_details(self):
        sel = self.tree.selection()
        if not sel:
            self.details_label.config(text="Select a task to view details.")
            return
        task_id = int(sel[0])
        t = next((x for x in self.task_manager.get_all() if x["id"] == task_id), None)
        if not t:
            self.details_label.config(text="Task not found.")
            return
        status = "Done" if t.get("completed") else "Pending"
        deadline = t.get("deadline") or "No deadline"
        notes = t.get("notes","")
        txt = f"Title: {t.get('title')}    |    Priority: {t.get('priority')}    |    Status: {status}\nDeadline: {deadline}\nNotes: {notes}"
        self.details_label.config(text=txt)

    # ---------------------------
    # Reminder thread
    # ---------------------------
    def _start_reminder_thread(self):
        self._stop_thread = False
        self.reminder_thread = threading.Thread(target=self._reminder_loop, daemon=True)
        self.reminder_thread.start()

    def _reminder_loop(self):
        while not getattr(self, "_stop_thread", True) is True:
            now = datetime.now()
            tasks = self.task_manager.get_all()
            for t in tasks:
                if t.get("completed"):
                    continue
                deadline = t.get("deadline")
                if not deadline:
                    continue
                try:
                    dt = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
                except Exception:
                    continue
                if t.get("reminded"):
                    continue
                # if deadline is within next REMINDER_LOOKAHEAD minutes and >= now
                if now <= dt <= now + timedelta(minutes=REMINDER_LOOKAHEAD):
                    # show notification
                    title = f"Task due: {t.get('title')}"
                    minutes_left = int((dt - now).total_seconds() // 60)
                    if minutes_left <= 0:
                        message = f"Due now: {t.get('title')}"
                    else:
                        message = f"Due in {minutes_left} minute(s): {t.get('title')}"
                    # mark reminded to avoid repeats
                    try:
                        self.task_manager.update_task(t["id"], reminded=True)
                    except Exception:
                        pass
                    try:
                        # schedule notification on main thread
                        self.after(100, lambda title=title, msg=message: notify(title, msg))
                    except Exception:
                        notify(title, message)
            # sleep small interval
            for _ in range(REMINDER_CHECK_INTERVAL):
                if getattr(self, "_stop_thread", False):
                    break
                time.sleep(1)

    def on_closing(self):
        self._stop_thread = True
        self.destroy()

# ---------------------------
# Dialog for Add/Edit
# ---------------------------
class TaskDialog(tk.Toplevel):
    def __init__(self, parent, title="Task", prefill=None):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self.result = None

        # Fields
        ttk.Label(self, text="Title:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.title_var = tk.StringVar(value=prefill.get("title") if prefill else "")
        ttk.Entry(self, textvariable=self.title_var, width=48).grid(row=0, column=1, padx=8, pady=6, columnspan=2)

        ttk.Label(self, text="Deadline (YYYY-MM-DD HH:MM):").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.deadline_var = tk.StringVar(value=prefill.get("deadline") if prefill else "")
        ttk.Entry(self, textvariable=self.deadline_var, width=24).grid(row=1, column=1, padx=8, pady=6, sticky="w")

        ttk.Label(self, text="Priority:").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.priority_var = tk.StringVar(value=prefill.get("priority") if prefill else "Medium")
        priorities = ("High","Medium","Low")
        prio_box = ttk.Combobox(self, textvariable=self.priority_var, values=priorities, state="readonly", width=20)
        prio_box.grid(row=2, column=1, padx=8, pady=6, sticky="w")

        ttk.Label(self, text="Notes:").grid(row=3, column=0, sticky="nw", padx=8, pady=6)
        self.notes_text = tk.Text(self, width=48, height=6)
        self.notes_text.grid(row=3, column=1, padx=8, pady=6, columnspan=2)
        if prefill:
            self.notes_text.insert("1.0", prefill.get("notes",""))

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=(0,8))
        ttk.Button(btn_frame, text="Save", command=self._on_save).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="Cancel", command=self._on_cancel).pack(side="left", padx=8)

        self.bind("<Return>", lambda e: self._on_save())
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_save(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Validation", "Title cannot be empty.")
            return
        deadline = self.deadline_var.get().strip()
        if deadline == "":
            deadline = None
        # no strict validation here; parent validates format
        priority = self.priority_var.get()
        notes = self.notes_text.get("1.0", "end").strip()
        self.result = (title, deadline, priority, notes)
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

# ---------------------------
# Main
# ---------------------------
def main():
    app = SmartToDoApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()
