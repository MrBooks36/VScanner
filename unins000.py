from winreg import DeleteKey, HKEY_CLASSES_ROOT
from sys import argv
from os.path import dirname, abspath, exists
from shutil import rmtree, copytree
from time import sleep
from subprocess import run

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
    run('start cmd /c C:\\Windows\\TEMP\\VScanner\\unins000.exe uninstall2', shell=True)

def uninstall2():
        file = open("C:\\Windows\\TEMP\\temp.asdf", "r")
        path = file.read()
        sleep(3)
        rmtree(path)
        return        

if __name__ == "__main__":
       if len(argv) > 1:
        if argv[1] == 'uninstall2': uninstall2()
       display_name = "Scan with VSanner"
       remove_context_menu_option(display_name)
       uninstall()