from sys import argv
from os.path import abspath
from components.scan import scan

print(argv)
if len(argv) == 1:
 from components import mainloop
else: scan(abspath(argv[1]))