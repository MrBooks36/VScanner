@echo off
del VScanner.exe
python -m nuitka --standalone --onefile --remove-output --enable-plugin=tk-inter --mingw64  main.py
powershell sleep 3
rename main.exe VScanner.exe

python -m nuitka --standalone --onefile --remove-output --windows-console-mode=disable --windows-uac-admin --mingw64  unins000.py

tar -vcjf VScanner.tar VScanner.exe unins000.exe

python -m nuitka --standalone --onefile --remove-output --enable-plugin=tk-inter --windows-console-mode=disable --windows-uac-admin --include-data-files=VScanner.tar=VScanner.tar --mingw64  installer.py

del unins000.exe
del VScanner.exe
del VScanner.tar
del main.exe