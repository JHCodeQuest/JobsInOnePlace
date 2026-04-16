import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import pandas as pd

DB = "jobs.db"

def fetch_jobs():
    with sqlite3.connect(DB) as conn:
        rows = conn.execute("""
            SELECT id, company, role, date_applied, status, job_url, notes
            FROM jobs
            ORDER BY id DESC
        """).fetchall()
    return rows

def get_columns():
    return ["id", "company", "role", "date_applied", "status", "job_url", "notes"]

def load_table():
    for row in tree.get_children():
        tree.delete(row)
    for row in fetch_jobs():
        tree.insert("", "end", values=row)

def export_csv():
    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")]
    )
    if not path:
        return
    df = pd.DataFrame(fetch_jobs(), columns=get_columns())
    df.to_csv(path, index=False)
    messagebox.showinfo("Exported", f"CSV saved to:\n{path}")

def export_excel():
    path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")]
    )
    if not path:
        return
    df = pd.DataFrame(fetch_jobs(), columns=get_columns())
    df.to_excel(path, index=False)
    messagebox.showinfo("Exported", f"Excel saved to:\n{path}")

root = tk.Tk()
root.title("Job Applications Viewer")

frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

tree = ttk.Treeview(frame, columns=get_columns(), show="headings", height=15)

for col in get_columns():
    tree.heading(col, text=col)
    tree.column(col, width=120, anchor="w")

scroll_y = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scroll_y.set)

tree.grid(row=0, column=0, sticky="nsew")
scroll_y.grid(row=0, column=1, sticky="ns")

frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)

button_frame = ttk.Frame(root, padding=10)
button_frame.pack(fill="x")

ttk.Button(button_frame, text="Refresh", command=load_table).pack(side="left", padx=5)
ttk.Button(button_frame, text="Export CSV", command=export_csv).pack(side="left", padx=5)
ttk.Button(button_frame, text="Export Excel", command=export_excel).pack(side="left", padx=5)

load_table()
root.mainloop()