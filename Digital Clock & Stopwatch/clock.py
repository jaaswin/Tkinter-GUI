import tkinter as tk
from tkinter import ttk
import time

# -----------------------------
# Digital Clock Function
# -----------------------------
def update_clock():
    current_time = time.strftime("%H:%M:%S")
    clock_label.config(text=current_time)
    clock_label.after(1000, update_clock)

# -----------------------------
# Stopwatch Functions
# -----------------------------
running = False
start_time = 0
elapsed_time = 0

def start_stopwatch():
    global running, start_time
    if not running:
        start_time = time.time() - elapsed_time
        update_stopwatch()
        running = True

def stop_stopwatch():
    global running
    if running:
        window.after_cancel(update_job)
        running = False

def reset_stopwatch():
    global elapsed_time, running
    stop_stopwatch()
    elapsed_time = 0
    stopwatch_label.config(text="00:00:00")

def update_stopwatch():
    global elapsed_time, update_job
    elapsed_time = time.time() - start_time
    formatted = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    stopwatch_label.config(text=formatted)
    update_job = window.after(1000, update_stopwatch)

# -----------------------------
# GUI Setup
# -----------------------------
window = tk.Tk()
window.title("Digital Clock & Stopwatch")
window.geometry("400x300")
window.configure(bg="#1e1e1e")

title = tk.Label(window, text="Digital Clock & Stopwatch", font=("Arial", 18, "bold"), fg="white", bg="#1e1e1e")
title.pack(pady=10)

# Clock UI
clock_label = tk.Label(window, font=("Arial", 40, "bold"), fg="#00ff00", bg="#1e1e1e")
clock_label.pack(pady=5)

# Stopwatch UI
stopwatch_label = tk.Label(window, text="00:00:00", font=("Arial", 40, "bold"), fg="#00c8ff", bg="#1e1e1e")
stopwatch_label.pack(pady=5)

# Buttons
button_frame = ttk.Frame(window)
button_frame.pack(pady=10)

ttk.Button(button_frame, text="Start", command=start_stopwatch).grid(row=0, column=0, padx=5)
ttk.Button(button_frame, text="Stop", command=stop_stopwatch).grid(row=0, column=1, padx=5)
ttk.Button(button_frame, text="Reset", command=reset_stopwatch).grid(row=0, column=2, padx=5)

update_clock()
window.mainloop()
