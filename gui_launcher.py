import sys
import threading
import json
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import egoweaver

class EgoWeaverGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("EgoWeaver | Behavioral Context Engine")
        self.geometry("900x650")
        ctk.set_appearance_mode("dark")
        
        # --- State Variables ---
        self.config = egoweaver.load_engine_config()
        self.input_path = ctk.StringVar(value=self.config['paths'].get('input', 'Input'))
        self.output_path = ctk.StringVar(value=self.config['paths'].get('output', 'output'))

        # --- Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="EgoWeaver", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo.grid(row=0, column=0, padx=20, pady=20)

        # VIP Editor Section
        self.vip_label = ctk.CTkLabel(self.sidebar, text="VIP Senders (Safe List):", font=ctk.CTkFont(weight="bold"))
        self.vip_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        
        self.vip_listbox = ctk.CTkTextbox(self.sidebar, height=150, width=200)
        self.vip_listbox.grid(row=2, column=0, padx=20, pady=10)
        self.vip_listbox.insert("1.0", "\n".join(self.config['filter_settings'].get('vip_senders', [])))

        self.score_label = ctk.CTkLabel(self.sidebar, text=f"Min Psych Score: {round(self.config['filter_settings']['min_psych_score'], 1)}")
        self.score_label.grid(row=3, column=0, padx=20, pady=(10, 0))
        
        self.score_slider = ctk.CTkSlider(self.sidebar, from_=0, to=10, command=self.update_score_label)
        self.score_slider.set(self.config['filter_settings']['min_psych_score'])
        self.score_slider.grid(row=4, column=0, padx=20, pady=10)

        # --- Main View ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Path Selection
        self.path_frame = ctk.CTkFrame(self.main_frame)
        self.path_frame.pack(fill="x", pady=10)

        self.in_label = ctk.CTkLabel(self.path_frame, textvariable=self.input_path, wraplength=400)
        self.in_label.pack(side="left", padx=10, pady=10)
        
        self.btn_in = ctk.CTkButton(self.path_frame, text="Browse Input", width=120, command=self.browse_input)
        self.btn_in.pack(side="right", padx=10)

        self.out_frame = ctk.CTkFrame(self.main_frame)
        self.out_frame.pack(fill="x", pady=10)
        
        self.out_label = ctk.CTkLabel(self.out_frame, textvariable=self.output_path)
        self.out_label.pack(side="left", padx=10, pady=10)

        self.btn_out = ctk.CTkButton(self.out_frame, text="Set Output", width=120, command=self.browse_output)
        self.btn_out.pack(side="right", padx=10)

        # Logs
        self.log_box = ctk.CTkTextbox(self.main_frame, height=300)
        self.log_box.pack(fill="both", expand=True, pady=10)

        self.start_btn = ctk.CTkButton(self.main_frame, text="START WEAVING", height=50, fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(weight="bold"), command=self.start_thread)
        self.start_btn.pack(fill="x", pady=10)

        sys.stdout = self # Redirect print()

    def update_score_label(self, val):
        self.score_label.configure(text=f"Min Psych Score: {round(val, 1)}")

    def browse_input(self):
        path = filedialog.askdirectory(title="Select folder containing .zip archives or stashed folders")
        if path: self.input_path.set(path)

    def browse_output(self):
        path = filedialog.askdirectory(title="Select where to save MD records")
        if path: self.output_path.set(path)

    def write(self, text):
        self.log_box.insert("end", text)
        self.log_box.see("end")

    def flush(self): pass

    def start_thread(self):
        if self.input_path.get() == "Not Selected":
            messagebox.showwarning("Selection Required", "Please select an input directory first.")
            return
        self.start_btn.configure(state="disabled")
        threading.Thread(target=self.run_weave, daemon=True).start()

    def run_weave(self):
        try:
            # Sync GUI settings to actual config object
            vips = self.vip_listbox.get("1.0", "end-1c").split('\n')
            self.config['filter_settings']['vip_senders'] = [v.strip() for v in vips if v.strip()]
            self.config['filter_settings']['min_psych_score'] = self.score_slider.get()
            self.config['paths']['input'] = self.input_path.get()
            self.config['paths']['output'] = self.output_path.get()
            
            # Save updated config back to file
            with open(egoweaver.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            
            print(f"\n[GUI] Config Saved. Starting EgoWeaver core...")
            egoweaver.main()
        except Exception as e:
            print(f"\n[CRITICAL ERROR] {e}")
        finally:
            self.start_btn.configure(state="normal")

if __name__ == "__main__":
    app = EgoWeaverGUI()
    app.mainloop()
