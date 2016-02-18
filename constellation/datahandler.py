#!/usr/bin/env python2
"""Data gathering and read-write access to persistent storage"""

import shelve
import os
import itertools

class Data_build(object):
    def __init__(self,maxrets=0):
        self.operating = False
        self.barebones = ' '
        self.maxrets = maxrets

    def open_hash(self,name):
        self.shelf = shelve.open(name,writeback=True)
        self.hashname = name
    
    def add_data(self,buf):
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
            return 2
    
    def get_devs(self,countname):
        for i in self.shelf[countname].keys():
            yield i
    
    def read_data(self,countname,devname,timest=0,begin=False):
        if timest = 0:
            index = 0
            for i, j in itertools.izip(self.shelf[countname][devname]['rate'],
                    self.shelf[countname][devname]['time']):
                if index <= self.maxrets:
                    yield (i,j)
                    index += 1
    
    def sync_hash(self):
        self.shelf.sync()

    def close_hash(self):
        self.shelf.close()

    def rem_hash(self):
        os.remove(self.hashname)





