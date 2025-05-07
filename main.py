import tkinter as tk
from tkinter import filedialog
import threading
from components.scan import scan_with_virustotal
from os import remove

def select_file_and_scan(scan_function):
    with open('log.tmp', 'w') as file:
        file.close()
    """Open a file dialog to select a file and then scan it using the provided scan function."""
    file_path = filedialog.askopenfilename()
    if file_path:
        result_text.delete(1.0, tk.END)  # Clear previous results

        # Use a separate thread to avoid blocking the GUI
        def thread_task():
            scan_function(file_path)

        
        thr = threading.Thread(target=thread_task)
        thr.start()
        while thr.is_alive():
            text = open('log.tmp', 'r').read()
            root.update()
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, text)
            result_text.config(state=tk.DISABLED)
        text = open('log.tmp', 'r').read()
        root.update()
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, text)  
        result_text.config(state=tk.DISABLED)  

def create_gui(scan_function):
    """Create and display the GUI."""
    global root
    root = tk.Tk()
    root.title("VirusTotal File Scanner")

    frame = tk.Frame(root)
    frame.pack(padx=20, pady=20)

    select_btn = tk.Button(frame, text="Select File", command=lambda: select_file_and_scan(scan_function))
    select_btn.pack(side=tk.TOP, fill=tk.X, pady=5)

    global result_text
    result_text = tk.Text(frame, height=20, width=80, state=tk.DISABLED)
    result_text.pack(side=tk.TOP, padx=5, pady=5)

    root.mainloop()
    try:
     remove('log.tmp')
    except: pass

create_gui(scan_with_virustotal)