from time import sleep
from os import listdir
from os.path import join, isfile, expanduser
from components.scan import scan

def get_files_in_directory(directory):
    """Returns a set of file paths in the given directory."""
    try:
        return set(join(directory, f) for f in listdir(directory) if isfile(join(directory, f)))
    except FileNotFoundError:
        print("Directory not found!")
        return set()

def monitor_downloads(download_dir, check_interval=5):
    """Monitor the specified directory for new files."""
    print(f"Monitoring directory: {download_dir}")
    
    previous_files = get_files_in_directory(download_dir)
    
    while True:
        sleep(check_interval)
        current_files = get_files_in_directory(download_dir)
        
        # Determine newly created files
        new_files = current_files - previous_files
        
        if new_files:
            for file_path in new_files:
                print(f"New file detected: {file_path}")
                scan(file_path)

        
        # Update the previous_files set
        previous_files = current_files

DOWNLOAD_DIR = expanduser("~/Downloads")
monitor_downloads(DOWNLOAD_DIR)