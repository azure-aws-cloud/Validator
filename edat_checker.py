# edat_checker.py
import os
import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET

def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_var.set(folder_path)

def validate_folder():
    output_text.delete(1.0, tk.END)
    folder_path = folder_var.get()

    if not folder_path:
        output_text.insert(tk.END, "[ERROR] No folder selected. Please browse and select a folder first.\n")
        return

    config_file_path = os.path.join(folder_path, "config", "config.xml")

    if not os.path.exists(config_file_path):
        output_text.insert(tk.END, f"[ERROR] File 'config.xml' not found at:\n{config_file_path}\n")
        return

    try:
        tree = ET.parse(config_file_path)
        root = tree.getroot()

        found = False
        for elem in root.iter("DECAutoName"):
            if elem.text and elem.text.strip().lower() == "false":
                output_text.insert(tk.END, "[FOUND] <DECAutoName>false</DECAutoName> found in config.xml\n")
                found = True
                break

        if not found:
            output_text.insert(tk.END, "[NOT FOUND] Tag <DECAutoName>false</DECAutoName> not found in config.xml\n")

    except ET.ParseError:
        output_text.insert(tk.END, "[ERROR] Failed to parse config.xml (malformed XML).\n")

def clear_messages():
    output_text.delete(1.0, tk.END)

# GUI Setup
app = tk.Tk()
app.title("EDAT Config Checker")

# Folder selection label
tk.Label(app, text="Choose EDAT folder:").grid(row=0, column=0, padx=10, pady=10, sticky="w")

# Folder path entry
folder_var = tk.StringVar()
folder_entry = tk.Entry(app, textvariable=folder_var, width=50)
folder_entry.grid(row=0, column=1, padx=10, pady=10)

# Buttons frame (Browse + Validate)
button_frame = tk.Frame(app)
button_frame.grid(row=0, column=2, padx=10, pady=10, sticky="e")

browse_button = tk.Button(button_frame, text="Browse", command=browse_folder, width=10)
browse_button.pack(side=tk.TOP, padx=5, pady=(0, 5))

validate_button = tk.Button(button_frame, text="Validate", command=validate_folder, width=10)
validate_button.pack(side=tk.TOP, padx=5)

# Output Text Area
output_text = tk.Text(app, height=15, width=80, wrap="word", bg="#f0f0f0")
output_text.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

# Clear Button
clear_button = tk.Button(app, text="Clear Messages", command=clear_messages)
clear_button.grid(row=2, column=2, padx=10, pady=5, sticky="e")

# Run App
app.mainloop()
