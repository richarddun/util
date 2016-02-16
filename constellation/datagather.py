#!/usr/local/bin/python2.7

import os
import sys
import subprocess
import re
import shelve

"""simple program to read newnslog counters and write to shelve"""

def counter_string_to_list_with_devno(string):
    """Takes newnslog counter input string, modifies the timestamp and returns a list representation of
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
        return new_list 
    else:
        pass


def rw_raw_data():
    #0 = Index, 1 = rtime (relative time), 2 = totalcount-val, 3 = delta, 4 = rate/sec, 5 = symbol-name 6 = &device-no, 7 = time

    # regexes for input handling
    detect_log_headers = re.compile('(reltime)|(Index)|(Performance)|(performance)|(Build)')
    strip_path_newnslog = re.compile('newnslo\S+')

    # locate log file
    input_file = os.path.join(os.getcwd(), args.newnslog)
    if not os.path.exists(input_file):
        print "\nCouldn't open newnslog file specified, halting.\n"
        sys.exit()

    #initialise command string for subprocess
    command_string = 'nsconmsg' + args.ver + ' -K ' + args.newnslog + ' -d current -g ' + args.type + ' -s disptime=1'

    #parse variables into list - because it is a bytestream passed from subprocess need to use splitlines()
    for line in subprocess.check_output([command_string], shell=True).splitlines():
        if not detect_log_headers.search(line):
            if line.strip():#make sure the line is _not_ empty
                outstring = counter_string_to_list_with_devno(line)
                sys.stdout.write(str(outstring) +'\n')

if __name__ == '__main__':
    rw_raw_data()

