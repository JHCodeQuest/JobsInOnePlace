import customtkinter as ctk
from tkinter import messagebox
import jobapps

# 1. Set the visual theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class JobTrackerGui(ctk.CTk):
    def __init__(self):
        super().__init__()

        jobapps.init_db()

        # Window Configuration
        self.title("Job Application Tracker v2.0")
        self.geometry("600x550")

        # Configure Grid Layout (2 columns: Sidebar and Content)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="JobTracker", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(20, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.appearance_mode_optionemenu.set("Dark")

        # --- Main Content Frame ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Form Inputs
        self.company_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Company Name", width=350)
        self.company_entry.grid(row=0, column=0, padx=20, pady=10)

        self.role_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Job Role", width=350)
        self.role_entry.grid(row=1, column=0, padx=20, pady=10)

        self.date_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Date Applied (YYYY-MM-DD)", width=350)
        self.date_entry.grid(row=2, column=0, padx=20, pady=10)

        # Modern Status Selector (Segmented Button instead of Entry)
        self.status_label = ctk.CTkLabel(self.main_frame, text="Application Status:")
        self.status_label.grid(row=3, column=0, pady=(10, 0))
        self.status_var = ctk.StringVar(value="Applied")
        self.status_seg = ctk.CTkSegmentedButton(self.main_frame, values=["Applied", "Interview", "Rejected", "Offer"],
                                                 variable=self.status_var)
        self.status_seg.grid(row=4, column=0, padx=20, pady=(5, 15))

        self.url_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Job URL", width=350)
        self.url_entry.grid(row=5, column=0, padx=20, pady=10)

        self.notes_text = ctk.CTkTextbox(self.main_frame, width=350, height=100)
        self.notes_text.grid(row=6, column=0, padx=20, pady=10)
        self.notes_text.insert("0.0", "Enter notes here...")

        # Action Buttons
        self.save_button = ctk.CTkButton(self.main_frame, text="Save Application", 
                                         command=self.submit_job, font=ctk.CTkFont(weight="bold"))
        self.save_button.grid(row=7, column=0, padx=20, pady=20)

    def submit_job(self):
        company = self.company_entry.get().strip()
        role = self.role_entry.get().strip()
        date_applied = self.date_entry.get().strip()
        status = self.status_var.get()
        job_url = self.url_entry.get().strip()
        notes = self.notes_text.get("0.0", "end").strip()

        if not company or not role or not date_applied:
            messagebox.showerror("Missing data", "Please fill in Company, Role, and Date.")
            return

        jobapps.add_job(company, role, date_applied, status, job_url, notes)
        messagebox.showinfo("Success", f"Saved {role} at {company}!")
        self.clear_form()

    def clear_form(self):
        self.company_entry.delete(0, 'end')
        self.role_entry.delete(0, 'end')
        self.date_entry.delete(0, 'end')
        self.url_entry.delete(0, 'end')
        self.notes_text.delete("0.0", "end")
        self.status_var.set("Applied")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

if __name__ == "__main__":
    app = JobTrackerGui()
    app.mainloop()