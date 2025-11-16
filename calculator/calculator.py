import tkinter as tk
import math

def click(btn):
    current = entry.get()
    if btn == "C":
        entry.delete(0, tk.END)
    elif btn == "=":
        try:
            expression = current.replace("sin", "math.sin")\
                                .replace("cos", "math.cos")\
                                .replace("tan", "math.tan")\
                                .replace("log", "math.log10")\
                                .replace("ln", "math.log")\
                                .replace("sqrt", "math.sqrt")\
                                .replace("^", "**")
            result = eval(expression)
            entry.delete(0, tk.END)
            entry.insert(tk.END, str(result))
        except:
            entry.delete(0, tk.END)
            entry.insert(tk.END, "Error")
    else:
        entry.insert(tk.END, btn)

root = tk.Tk()
root.title("Scientific Calculator")

root.configure(bg="#181818")

entry = tk.Entry(root, width=25, font=("Consolas", 22), borderwidth=5, relief="sunken", bg="#000", fg="#0f0", justify="right")
entry.grid(row=0, column=0, columnspan=6, padx=10, pady=10)

buttons = [
    ["sin", "cos", "tan", "log", "ln", "sqrt"],
    ["7", "8", "9", "/", "^", "("],
    ["4", "5", "6", "*", "%", ")"],
    ["1", "2", "3", "-", "C", "π"],
    ["0", ".", "=", "+", "e", "**"]
]

for r, row in enumerate(buttons):
    for c, btn in enumerate(row):
        color = "#333"
        if btn in ["=", "+", "-", "*", "/", "C"]:
            color = "#444"
        if btn == "=":
            color = "#0052cc"

        tk.Button(root, text=btn, width=6, height=2, font=("Consolas", 18), bg=color, fg="white",
                  command=lambda b=btn: click(b if b not in ["π","e"] else ("3.14159" if b=="π" else "2.71828"))
        ).grid(row=r+1, column=c, padx=3, pady=3)

root.mainloop()
