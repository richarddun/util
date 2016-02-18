#!/usr/bin/env python2
"""Data gathering and read-write access to persistent storage"""

import shelve
import os

class Data_build(object):
    def __init__(self):
        self.operating = False
        self.barebones = ' '

    def open_hash(self,name):
        self.shelf = shelve.open(name)
        self.hashname = name

    def add_data(self,buf):
        self.rate = buf[0]
        self.counter_name = buf[1]
        self.devname = buf[2]
        self.timestamp = buf[3]
        if not self.counter_name in self.shelf:
            self.shelf[self.counter_name] = {self.devname:{'rate':[],'time':[]}}


