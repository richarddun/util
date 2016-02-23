#!/usr/bin/env python2
"""Data gathering and read-write access to persistent storage"""

import shelve
import os
import itertools
import subprocess
from time import datetime

class Data_build(object):
    """Class to interact with python shelve to build/read/write/destroy shelves 
       based on need"""
    def __init__(self,maxrets=0):
        self.operating = False
        self.barebones = ' '
        self.maxrets = maxrets

    def open_hash(self,name):
        """Open a shelve instance"""
        self.shelf = shelve.open(name,writeback=True)
        self.hashname = name
    
    def add_data(self,buf):
        """Add data passed from list containing specific values to a shelve record
           Values expected : 0 - Rate (int),1 - Name (str), 2 - Dev_name (str), 
           3 - Timestamp (int)"""
        if len(buf) == 4:
            self.rate = buf[0]
            self.counter_name = buf[1]
            self.devname = buf[2]
            self.timestamp = buf[3]
            if not self.counter_name in self.shelf:
                self.shelf[self.counter_name] = {self.devname:{'rate':[],'time':[]}}
            else:
                self.shelf[self.counter_name][self.devname]['rate'].append(self.rate)
                self.shelf[self.counter_name][self.devname]['time'].append(self.timestamp)
        else:
            raise ValueError('Attempted to add more or less than 4 items as shelve record')
            return 2
    
    def get_devs(self,countname):
        """Read shelve keys, return 'Devname' ; Devname is a string identifying an entity
           to track, and update in the shelve instance"""
        for i in self.shelf[countname].keys():
            yield i
    
    def read_data(self,countname,devname,timest=0,begin=False):
        """Read and return data from the shelve instance.
           Accepts countername, device name and timestamp.
           Iterates through a hash, stopping at maxrets (
           total number of records to return)"""
        if timest = 0:
            index = 0
            for i, j in itertools.izip(self.shelf[countname][devname]['rate'],
                    self.shelf[countname][devname]['time']):
                if index <= self.maxrets:
                    yield (i,j)
                    index += 1
    
    def sync_hash(self):
        """Writeback will be enabled, convenience function to sync the 
           shelve instance"""
        self.shelf.sync()

    def close_hash(self):
        """Convenience function to close the shelve instance"""
        self.shelf.close()

    def rem_hash(self):
        """Convenience function to remove the shelve .db file"""
        os.remove(self.hashname)

class Nstools(object):
    """NS Tools class instance.  Used to parse and manipulate
       NetScaler newnslog counter output when run with the 
       'nsconmsg' log file reader"""
    def __init__(self,nslog,nsver,countlist):
        #initialise command string for subprocess
        self.nslog = nslog
        self.nsver = nsver
        self.countlist = countlist
        self.command_string = 'nsconmsg' + self.nsver + ' -K ' + self.nslog + \
            ' -d current' + ' -s disptime=1' #TODO - modify to build larger
            #pattern set
        
    def counter_string_to_list_with_devno(string):
        """Takes counter input string, modifies the timestamp and 
        returns a list representation of the string"""
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
        #TODO - convert time string to epoch 
        #before passing back
        else:
            pass

    def nratechecker():
        """Netscaler specific log reading method.  References
        counter_string_to_list_with_devno()
        """
        
        checklist = ['master_cpu_use','mgmt_cpu_use']
        #checklist put here for no reason, other than a reminder
        #for now
        
        #0 = Index, 1 = rtime (relative time), 2 = totalcount-val, 
        #3 = delta, 4 = rate/sec, 5 = symbol-name 6 = &device-no, 7 = time

        # regexes for input handling
        detect_log_headers = re.compile('(reltime)|(Index)|
                (Performance)|(performance)|(Build)')
        strip_path_newnslog = re.compile('newnslo\S+')
        # locate log file
        input_file = os.path.join(os.getcwd(), self.nslog)
        if not os.path.exists(input_file):
            raise IOError('Input file not found')
            return 3

        #parse variables into list - because it is a bytestream passed 
        #from subprocess need to use splitlines()

        for line in subprocess.check_output([self.command_string], 
                shell=True).splitlines():
            if not detect_log_headers.search(line):
                if line.strip():#make sure the line is _not_ empty
                    outstring = self.counter_string_to_list_with_devno(line)
                    yield outstring


#TODO - work further on flow of data from logger to hash
#     - work on logic with class instantiation and 
#       utilisation of classes in main program flow
