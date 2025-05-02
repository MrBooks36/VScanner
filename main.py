from sys import argv
from components.scan import scan

if len(argv) == 1:
 from components import mainloop
else: scan(argv[1])