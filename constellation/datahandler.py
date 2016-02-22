#!/usr/bin/env python2
"""Data gathering and read-write access to persistent storage"""

import shelve
import os
import itertools

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
        """Read and return data from the shelve instance"""
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

    def close_hash(self
        """Convenience function to close the shelve instance"""
        self.shelf.close()

    def rem_hash(self):
        """Convenience function to remove the shelve .db file"""
        os.remove(self.hashname)

class Nstools(object):
    def __init__(self,nslog,nsver,countlist):
        #initialise command string for subprocess
        command_string = 'nsconmsg' + nsver + ' -K ' + nslog + \
            ' -d current' + ' -s disptime=1'


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
        else:
            pass




