#!/usr/bin/env python2
"""Main program control and logic"""

import argparse
import os
import sys
import subprocess
import re
from datahandler import *
from display import *


def counter_string_to_list_with_devno(string):
    """Takes newnslog counter input string, modifies the timestamp (which is space
    seperated and not easy to add to a list) and returns a list representation of
    the string"""
    if len(string.split()) == 11:
        new_list = string.split()[0:6]
        add_list = string.split()[7:11]
        new_list.append(" ".join(add_list))
        return new_list
    elif len(string.split()) == 12:
        new_list = string.split()[0:7]
        add_list = string.split()[7:12]
        new_list.append(" ".join(add_list))
        return new_list #new_list[4:]
    else:
        pass


def ratechecker():
    checklist = ['master_cpu_use','mgmt_cpu_use']
    #0 = Index, 1 = rtime (relative time), 2 = totalcount-val, 3 = delta, 4 = rate/sec, 5 = symbol-name 6 = &device-no, 7 = time

    # regexes for input handling
    detect_log_headers = re.compile('(reltime)|(Index)|(Performance)|(performance)|(Build)')
    strip_path_newnslog = re.compile('newnslo\S+')

    #handle user input
    parser = argparse.ArgumentParser(description ='Rate count visualiser given a counter file', epilog='Options can be shortened. e.g. constellation -n newnslog.71 -v 105')
    group1 = parser.add_argument_group('required arguments')
    group1.add_argument("-ver", choices=['101','105','110'],help="Newnslog version",required=True)
    group1.add_argument("-newnslog", help="Newnslog to parse",required=True,metavar='PATH')
    args = parser.parse_args()

    # locate log file
    input_file = os.path.join(os.getcwd(), args.newnslog)
    if not os.path.exists(input_file):
        print "\nCouldn't open newnslog file specified, halting.\n"
        sys.exit()

    #initialise command string for subprocess
    command_string = 'nsconmsg' + args.ver + ' -K ' + args.newnslog + ' -d current' + ' -s disptime=1'

    dataspool = Data_build()
    dataspool.open_hash(args.newnslog)

    #parse variables into list - because it is a bytestream passed from subprocess need to use splitlines()
    for line in subprocess.check_output([command_string], shell=True).splitlines():
        if not detect_log_headers.search(line):
            if line.strip():#make sure the line is _not_ empty
                outstring = counter_string_to_list_with_devno(line)
                sys.stdout.write(str(outstring) +'\n')

if __name__ == '__main__':
    ratechecker()

