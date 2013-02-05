#################################################
#  myrender.py  
#  python script for take an xml file and convert it to an html file
#  that the browser can render
#
#  Jan 1, 2013 JMO
#    Created
#    Very elementary just wrap the file:
#    <html><body> xml file content </body></html>
#
####################################

import sys
import os
import os.path
import string
import getopt
import traceback

def showUsage():
    print "Converts an xml file to an html file"
    print ""
    print "Syntax: python myrender.py inputxml outputhtml"
    print "Options:"
    print "   None"

def main():    
    #No need for parseCommandLine() routine until we add some options
    if len(sys.argv[1:]) != 2:
        showUsage()
        return

    fnamein = sys.argv[1]
    fnameout = sys.argv[2]

    fp = open(fnamein,"r")
    x = fp.read() #read the entire file
    fp.close()

    fp = open(fnameout,'w')
    fp.write("<html>\n<body>\n\n")
    fp.write(x)
    fp.write("\n\n</body></html>\n")
    fp.close()
             
if __name__ == '__main__':
    main()
