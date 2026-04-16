import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import jobapps
import pandas as pd
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class JobTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Job Tracker Pro")
        self.geometry("1100x800")
        jobapps.init_db()

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)
        self.tabview.add("Entry")
        self.tabview.add("View & Manage")
        
        self.build_entry_tab()
        self.build_view_tab()

    def build_entry_tab(self):
        tab = self.tabview.tab("Entry")
        frame = ctk.CTkFrame(tab)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.company_entry = ctk.CTkEntry(frame, placeholder_text="Company Name", width=400)
        self.company_entry.pack(pady=10)

        self.role_entry = ctk.CTkEntry(frame, placeholder_text="Role", width=400)
        self.role_entry.pack(pady=10)

        self.date_entry = ctk.CTkEntry(frame, placeholder_text="Date (YYYY-MM-DD)", width=400)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(pady=10)

        self.status_var = ctk.StringVar(value="Applied")
        self.status_seg = ctk.CTkSegmentedButton(frame, values=["Applied", "Interview", "Rejected", "Offer"], variable=self.status_var)
        self.status_seg.pack(pady=10)

        self.url_entry = ctk.CTkEntry(frame, placeholder_text="Job URL", width=400)
        self.url_entry.pack(pady=10)

        self.notes_text = ctk.CTkTextbox(frame, height=100, width=400)
        self.notes_text.pack(pady=10)

        ctk.CTkButton(frame, text="Save Job", command=self.save_job, fg_color="#27ae60").pack(pady=20)

    def build_view_tab(self):
        tab = self.tabview.tab("View & Manage")
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0)
        style.configure("Treeview.Heading", background="#333", foreground="white", relief="flat")
        
        self.tree = ttk.Treeview(tab, columns=("id", "company", "role", "date", "status"), show="headings")
        for col in ("id", "company", "role", "date", "status"):
            self.tree.heading(col, text=col.title())
        self.tree.column("id", width=50)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Management Button Frame
        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(btn_frame, text="Refresh", command=self.load_table).grid(row=0, column=0, padx=5, pady=10)
        ctk.CTkButton(btn_frame, text="Delete Selected", command=self.delete_selected, fg_color="#c0392b").grid(row=0, column=1, padx=5, pady=10)
        ctk.CTkButton(btn_frame, text="Import CSV", command=self.import_csv).grid(row=0, column=2, padx=5, pady=10)
        ctk.CTkButton(btn_frame, text="Export CSV", command=self.export_csv).grid(row=0, column=3, padx=5, pady=10)
        ctk.CTkButton(btn_frame, text="Template", command=self.download_template).grid(row=0, column=4, padx=5, pady=10)
        
        self.load_table()

    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a job from the table to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected entry?"):
            for item in selected_item:
                job_id = self.tree.item(item)['values'][0]
                jobapps.delete_job(job_id)
            self.load_table()

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if path:
            try:
                df = pd.read_csv(path)
                
                # --- NaN Handling ---
                # 1. Drop rows that are completely empty
                df.dropna(how='all', inplace=True)
                
                # 2. Drop rows that specifically have no company or role (useless entries)
                df.dropna(subset=['company', 'role'], inplace=True)
                
                # 3. Fill remaining secondary NaNs with empty strings
                df.fillna("", inplace=True)

                for _, r in df.iterrows():
                    jobapps.add_job(r['company'], r['role'], r['date_applied'], r.get('status', 'Applied'), r.get('job_url', ''), r.get('notes', ''))
                
                self.load_table()
                messagebox.showinfo("Import Success", f"Imported {len(df)} jobs successfully (removed invalid/empty entries).")
            except Exception as e:
                messagebox.showerror("Import Error", f"Could not process CSV: {e}")

    # ... (Keep save_job, load_table, export_csv, and download_template same as before)
    def save_job(self):
        jobapps.add_job(self.company_entry.get(), self.role_entry.get(), self.date_entry.get(), self.status_var.get(), self.url_entry.get(), self.notes_text.get("0.0", "end"))
        messagebox.showinfo("Success", "Job Saved!")
        self.load_table()

    def load_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for row in jobapps.fetch_jobs():
            self.tree.insert("", "end", values=row[:5])

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            df = pd.DataFrame(jobapps.fetch_jobs(), columns=["ID", "Company", "Role", "Date", "Status", "URL", "Notes"])
            df.to_csv(path, index=False)
            messagebox.showinfo("Exported", "Data saved.")

    def download_template(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="template.csv")
        if path:
            pd.DataFrame(columns=["company", "role", "date_applied", "status", "job_url", "notes"]).to_csv(path, index=False)
            messagebox.showinfo("Success", "Template saved.")

if __name__ == "__main__":
    app = JobTrackerApp()
    app.mainloop()