import os
import re
import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET
import netifaces

def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_var.set(folder_path)

def get_ethernet_mac_address():
    """
    Get MAC address of the first physical Ethernet interface.
    Filters out virtual, loopback, and wireless interfaces.
    """
    try:
        for interface in netifaces.interfaces():
            # Skip non-physical interfaces
            if any(bad in interface.lower() for bad in ['loopback', 'wifi', 'wlan', 'vmware', 'virtual', 'bluetooth']):
                continue
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_LINK in addrs:
                mac = addrs[netifaces.AF_LINK][0].get('addr')
                if mac and len(mac.split(":")) == 6 and not mac.startswith("00:00:00"):
                    # Format MAC (uppercase, dashes)
                    return re.sub(r"[:]", "-", mac.upper())
    except Exception:
        return None
    return None

def insert_message(text, tag):
    output_text.insert(tk.END, text + "\n", tag)
    output_text.see(tk.END)  # Scroll to bottom

def check_eaton_attribute(xml_file_path):
    """
    Check if any element has UPSName attribute starting with 'eaton' (case-insensitive).
    Returns True if found, else False.
    """
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        for elem in root.iter():
            upsname = elem.attrib.get("UPSName")
            if upsname and upsname.lower().startswith("eaton"):
                return True
        return False
    except ET.ParseError:
        insert_message(f"[ERROR] Failed to parse XML file:\n{xml_file_path}", "error")
        return False
    except Exception as e:
        insert_message(f"[ERROR] Unexpected error checking XML file:\n{xml_file_path}\n{e}", "error")
        return False

def validate_folder():
    output_text.delete(1.0, tk.END)
    folder_path = folder_var.get()

    if not folder_path:
        insert_message("[ERROR] No folder selected. Please browse and select a folder first.", "error")
        return

    # === Step 1: Validate config/config.xml ===
    config_file_path = os.path.join(folder_path, "config", "config.xml")
    if not os.path.exists(config_file_path):
        insert_message(f"[ERROR] File 'config.xml' not found at:\n{config_file_path}", "error")
    else:
        try:
            tree = ET.parse(config_file_path)
            root = tree.getroot()

            found = False
            for elem in root.iter("DECAutoName"):
                if elem.text and elem.text.strip().lower() == "false":
                    insert_message("[FOUND] <DECAutoName>false</DECAutoName> found in config.xml", "success")
                    found = True
                    break

            if not found:
                insert_message("[NOT FOUND] Tag <DECAutoName>false</DECAutoName> not found in config.xml", "error")

        except ET.ParseError:
            insert_message("[ERROR] Failed to parse config.xml (malformed XML).", "error")

    output_text.insert(tk.END, "\n")

    # === Step 2: Validate lic/<mac>_EDT.lic ===
    lic_dir = os.path.join(folder_path, "lic")
    mac_address = get_ethernet_mac_address()

    if not mac_address:
        insert_message("[ERROR] Could not determine MAC address of an Ethernet adapter.", "error")
        return

    lic_file_name = f"{mac_address}_EDT.lic"
    lic_file_path = os.path.join(lic_dir, lic_file_name)

    if not os.path.exists(lic_dir):
        insert_message(f"[ERROR] 'lic' folder not found at: {lic_dir}", "error")
    elif not os.path.isfile(lic_file_path):
        insert_message(f"[ERROR] License file '{lic_file_name}' not found in 'lic' folder.", "error")
    else:
        insert_message(f"[VALID] License file '{lic_file_name}' found and valid.", "success")

    output_text.insert(tk.END, "\n")

    # === Step 3: Check install/pre_scripts/EDAT_CustomAttributesEDATMigration.xml for UPSName starting with 'eaton' ===
    pre_scripts_dir = os.path.join(folder_path, "install", "pre_scripts")
    migration_xml = os.path.join(pre_scripts_dir, "EDAT_CustomAttributesEDATMigration.xml")

    if not os.path.exists(pre_scripts_dir):
        insert_message(f"[ERROR] 'install\\pre_scripts' folder not found at:\n{pre_scripts_dir}", "error")
    elif not os.path.isfile(migration_xml):
        insert_message(f"[ERROR] File 'EDAT_CustomAttributesEDATMigration.xml' not found in:\n{pre_scripts_dir}", "error")
    else:
        has_eaton_upsname = check_eaton_attribute(migration_xml)
        if has_eaton_upsname:
            insert_message("[FOUND] UPSName attribute starting with 'eaton' found in EDAT_CustomAttributesEDATMigration.xml", "success")
        else:
            insert_message("[NOT FOUND] No UPSName attribute starting with 'eaton' found in EDAT_CustomAttributesEDATMigration.xml", "error")

def clear_messages():
    output_text.delete(1.0, tk.END)

# ===================== GUI Setup =====================
app = tk.Tk()
app.title("EDAT Config & License Checker")

# Row 0: Folder selection label
tk.Label(app, text="Choose EDAT folder:").grid(row=0, column=0, padx=10, pady=10, sticky="w")

# Row 0: Folder entry
folder_var = tk.StringVar()
folder_entry = tk.Entry(app, textvariable=folder_var, width=50)
folder_entry.grid(row=0, column=1, padx=10, pady=10)

# Row 0: Button frame (Browse + Validate)
button_frame = tk.Frame(app)
button_frame.grid(row=0, column=2, padx=10, pady=10, sticky="e")

browse_button = tk.Button(button_frame, text="Browse", command=browse_folder, width=10)
browse_button.pack(side=tk.TOP, padx=5, pady=(0, 5))

validate_button = tk.Button(button_frame, text="Validate", command=validate_folder, width=10)
validate_button.pack(side=tk.TOP, padx=5)

# Row 1: Output text area
output_text = tk.Text(app, height=20, width=80, wrap="word", bg="#f0f0f0")
output_text.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

# Define tags for colored messages
output_text.tag_configure("error", foreground="red")
output_text.tag_configure("success", foreground="green")

# Row 2: Clear button
clear_button = tk.Button(app, text="Clear Messages", command=clear_messages)
clear_button.grid(row=2, column=2, padx=10, pady=5, sticky="e")

app.mainloop()
