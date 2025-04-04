import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import re

# This code is a simple GUI application that allows users to input text and automatically type it out
class AutoTyper:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Auto Typer")
        self.running = False
        self.scheduled_event = None
        self.create_widgets()

    def create_widgets(self):
        # Text Entry Frame with "Select All" Button
        text_frame = ttk.LabelFrame(self.root, text="Enter Code/Text")
        text_frame.pack(padx=10, pady=5, fill="both")
        
        # Text widget
        self.text_entry = tk.Text(text_frame, height=15, width=60, wrap="none")
        self.text_entry.pack(side="left", fill="both", expand=True)
        
        # Scrollbar for text widget
        scrollbar = ttk.Scrollbar(text_frame, command=self.text_entry.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_entry.config(yscrollcommand=scrollbar.set)
        
        # Button frame for additional text options
        text_btn_frame = ttk.Frame(self.root)
        text_btn_frame.pack(padx=10, pady=(0,5), fill="x")
        
        select_all_btn = ttk.Button(text_btn_frame, text="Select All", command=self.select_all_text)
        select_all_btn.pack(side="left")

        # Configuration Frame
        config_frame = ttk.Frame(self.root)
        config_frame.pack(padx=10, pady=5, fill="x")
        
        # Delay Configuration
        ttk.Label(config_frame, text="Delay (s):").grid(row=0, column=0, sticky="w")
        self.delay_entry = ttk.Entry(config_frame, width=5)
        self.delay_entry.insert(0, "5")
        self.delay_entry.grid(row=0, column=1, sticky="w")
        
        # Background typing option: minimize on start
        self.minimize_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="Minimize on Start", variable=self.minimize_var).grid(row=0, column=2, padx=10)
        
        # Tab Handling Options:
        # Radio buttons to choose between replacing tabs with spaces or removing them.
        self.tab_option = tk.StringVar(value="replace")  # options: "replace" or "remove"
        tab_frame = ttk.LabelFrame(config_frame, text="Tab Handling")
        tab_frame.grid(row=1, column=0, columnspan=3, pady=5, sticky="w")
        
        ttk.Radiobutton(tab_frame, text="Replace with spaces", variable=self.tab_option, value="replace",
                        command=self.toggle_tab_entry).grid(row=0, column=0, padx=5, sticky="w")
        ttk.Radiobutton(tab_frame, text="Remove tabs", variable=self.tab_option, value="remove",
                        command=self.toggle_tab_entry).grid(row=0, column=1, padx=5, sticky="w")
        
        self.tab_spaces = ttk.Entry(tab_frame, width=3)
        self.tab_spaces.insert(0, "4")
        self.tab_spaces.grid(row=0, column=2, sticky="w")
        
        # Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Typing", command=self.start_typing)
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_typing, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

    def select_all_text(self):
        # Selects all text in the text widget
        self.text_entry.tag_add("sel", "1.0", "end")
        self.text_entry.focus_set()

    def toggle_tab_entry(self):
        # Only enable the spaces entry if "replace" is selected
        if self.tab_option.get() == "replace":
            self.tab_spaces.config(state="normal")
        else:
            self.tab_spaces.config(state="disabled")

    def clean_text(self, text):
        # First, trim unnecessary whitespace for each line:
        lines = text.splitlines()
        cleaned_lines = [line.strip() for line in lines if line.strip() != ""]
        cleaned_text = "\n".join(cleaned_lines)
        return cleaned_text

    def process_text(self, text):
        # Clean text from unnecessary whitespace first.
        text = self.clean_text(text)
        # Process tabs based on the chosen option.
        if self.tab_option.get() == "replace":
            try:
                spaces = int(self.tab_spaces.get())
            except ValueError:
                spaces = 4
            text = text.replace("\t", " " * spaces)
        elif self.tab_option.get() == "remove":
            text = text.replace("\t", "")
        return text

    def start_typing(self):
        text = self.text_entry.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showwarning("Warning", "Please enter some text to type!")
            return
        
        try:
            delay = float(self.delay_entry.get())
        except ValueError:
            delay = 5.0
        
        text = self.process_text(text)
        self.typing_queue = list(text)
        
        messagebox.showinfo("Info", f"Typing starts in {delay} seconds. Focus the target window!")
        
        # Minimize the window if background typing is selected
        if self.minimize_var.get():
            self.root.iconify()
        
        self.root.after(int(delay * 1000), self.type_next_character)
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.running = True

    def type_next_character(self):
        if not self.running or not self.typing_queue:
            self.stop_typing()
            return
        
        char = self.typing_queue.pop(0)
        try:
            if char == "\n":
                pyautogui.press("enter")
            else:
                pyautogui.write(char, interval=0.001)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.stop_typing()
            return
        
        self.scheduled_event = self.root.after(10, self.type_next_character)

    def stop_typing(self):
        self.running = False
        if self.scheduled_event:
            self.root.after_cancel(self.scheduled_event)
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        # Restore the window if it was minimized
        if self.minimize_var.get():
            self.root.deiconify()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoTyper(root)
    root.mainloop()
