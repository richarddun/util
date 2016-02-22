#!/usr/bin/env python2
"""Main program control and logic"""

import argparse
import os
import sys
import subprocess
import re
from datahandler import *
from display import *


#handle user input
parser = argparse.ArgumentParser(description ='Rate count visualiser')
group1 = parser.add_argument_group('required arguments')
group1.add_argument("-ns", metavar='Use if logfile is newnslog')
group1.add_argument("-ver", choices=['101','105','110'],
        help="Newnslog version")
group1.add_argument("-infile", help="Logfile to parse",
        required=True,metavar='PATH')
args = parser.parse_args()

logfile = args.infile

dataspool = Data_build()
dataspool.open_hash(logfile)

def nratechecker(nslog,nsver,countlist):
    """Netscaler specific log reader.  Takes 3 arguments :
       nslog = newnslog file (zipped or unzipped),
       nsver = version of NetScaler which created the file
       countlist = list of counters to include when reading"""
    
    checklist = ['master_cpu_use','mgmt_cpu_use']
    #0 = Index, 1 = rtime (relative time), 2 = totalcount-val, 
    #3 = delta, 4 = rate/sec, 5 = symbol-name 6 = &device-no, 7 = time

    # regexes for input handling
    detect_log_headers = re.compile('(reltime)|(Index)|
            (Performance)|(performance)|(Build)')
    strip_path_newnslog = re.compile('newnslo\S+')
    # locate log file
    input_file = os.path.join(os.getcwd(), args.newnslog)
    if not os.path.exists(input_file):
        print "\nCouldn't open newnslog file specified, halting.\n"
        sys.exit()


    #parse variables into list - because it is a bytestream passed 
    #from subprocess need to use splitlines()

    for line in subprocess.check_output([command_string], 
            shell=True).splitlines():
        if not detect_log_headers.search(line):
            if line.strip():#make sure the line is _not_ empty
                outstring = counter_string_to_list_with_devno(line)
                sys.stdout.write(str(outstring) +'\n')





















#if __name__ == '__main__':
#    ratechecker()

