from winreg import DeleteKey, HKEY_CLASSES_ROOT, OpenKey, CloseKey, HKEY_LOCAL_MACHINE, KEY_ALL_ACCESS
from sys import argv
from os.path import dirname, abspath, exists
from os import remove, getlogin
from shutil import rmtree, copytree
from time import sleep
from subprocess import run

def remove_registry_entry(app_name):
    # Open the registry key for installed applications
    key_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'
    
    try:
        reg_key = OpenKey(HKEY_LOCAL_MACHINE, key_path, 0, KEY_ALL_ACCESS)
        
        # Delete the subkey for the application
        DeleteKey(reg_key, app_name)
        
        print(f'Successfully removed {app_name} from installed apps list.')
    except FileNotFoundError:
        print(f'App name "{app_name}" not found. No changes made.')
    except Exception as e:
        print(f'Failed to remove {app_name} from installed apps list: {e}')
    finally:
        CloseKey(reg_key)

def remove_context_menu_option(display_name):
    try:
        DeleteKey(HKEY_CLASSES_ROOT, r'*\shell\{}\command'.format(display_name))
        DeleteKey(HKEY_CLASSES_ROOT, r'*\shell\{}'.format(display_name))
        print(f'Successfully removed context menu item: "{display_name}"')
    except FileNotFoundError:
        print(f'Context menu item "{display_name}" not found.')
    except WindowsError as e:
        print(f"Error modifying registry: {e}")

def uninstall():
    script_directory = dirname(abspath(argv[0]))
    if exists("C:\\Windows\\TEMP\\VScanner"): rmtree("C:\\Windows\\TEMP\\VScanner")
    copytree(script_directory, "C:\\Windows\\TEMP\\VScanner")
    file = open("C:\\Windows\\TEMP\\temp.asdf", "w")
    file.write(script_directory)
    try:
     remove(f'c:\\users\\{getlogin()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\VScanner.lnk')
    except: pass 
    try:
        remove('C:/ProgramData/Microsoft/Windows/Start Menu/Programs/VScanner.lnk')
    except: pass    
    remove_registry_entry('Vscanner')
    run('start cmd /c C:\\Windows\\TEMP\\VScanner\\unins000.exe uninstall2', shell=True)

def uninstall2():
        file = open("C:\\Windows\\TEMP\\temp.asdf", "r")
        path = file.read()
        sleep(3)
        rmtree(path)
        rmtree(path)
        return        

if __name__ == "__main__":
       if len(argv) > 1:
        if argv[1] == 'uninstall2': uninstall2()
       display_name = "Scan with VSanner"
       remove_context_menu_option(display_name)
       uninstall()