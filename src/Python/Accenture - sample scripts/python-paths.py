import sys
import os
 
options = [ "chars", "words", "lines" ]
 
try:
 
    3 == len(sys.argv)
    option = sys.argv[1]
 
    if not option in options:
        print("Sorry, that option " + option + " is not supported.")
        print("Supported options : "  + ",".join(options))
 
        exit(0)
 
     
    cur_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    with open(os.path.join(cur_dir, sys.argv[2]), "r") as f:
        content = f.readlines()
        print(content)
 
except Exception as e:
    print(e)
	
	