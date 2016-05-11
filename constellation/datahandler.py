#!/usr/bin/env python2
"""Data gathering and read-write access to persistent storage"""

from __future__ import division
import shelve
import os
import subprocess
import time
import re
import pdb

class Data_build(object):
    """Class to interact with python shelve to build/read/write/destroy shelves 
       based on need"""
    def __init__(self,maxrets=0):
        self.maxtval = 0 #maximum time value (end of counters) 100 on x index
        self.mintval = 4102444800 #minimum time value (start) 0 on x index

    def open_hash(self,name):
        """Open a shelve instance"""
        self.shelf = shelve.open(name,writeback=True)
        self.hashname = name

    def add_data(self,buf):
        """Add data passed from list containing specific values to a shelve record
           Values expected : 0 - Value (int),1 - Name (str), 2 - Dev_name (str), 
           3 - Timestamp (int)
           Also note max/min val/time while reading data
        """
        tempval = []
        temptim = []
        if buf[1] == 'sys_cur_duration_sincestart':
            if 'timestamps' in self.shelf.keys():
                temptim = self.shelf['timestamps']
                temptim.append(buf[2])
                self.shelf['timestamps'] = temptim
            else:
                temptim.append(buf[2])
                self.shelf['timestamps'] = temptim
        elif len(buf) == 4:
            self.value = buf[0]
            self.counter_name = buf[1]
            self.devname = buf[2]
            self.timestamp = buf[3]
            #take a note of max/min of time/values for later
            #doing it here helps improve performance overall
            if self.timestamp > self.maxtval:
                self.maxtval = self.timestamp
            elif self.timestamp < self.mintval:
                self.mintval = self.timestamp
            #write info to shelf
            if not self.counter_name in self.shelf:
                self.shelf[self.counter_name] = {self.devname:{'value':[],'time':[]}}
                tempval = self.shelf[self.counter_name][self.devname]['value']
                tempval.append(int(self.value))
                self.shelf[self.counter_name][self.devname]['value'] = tempval
                
                temptim = self.shelf[self.counter_name][self.devname]['time']
                temptim.append(int(self.timestamp))
                self.shelf[self.counter_name][self.devname]['time'] = temptim

            if not self.devname in self.shelf[self.counter_name]:
                self.shelf[self.counter_name].update({self.devname:{'value':[],'time':[]}})

                tempval = self.shelf[self.counter_name][self.devname]['value']
                tempval.append(int(self.value))
                self.shelf[self.counter_name][self.devname]['value'] = tempval
                
                temptim = self.shelf[self.counter_name][self.devname]['time']
                temptim.append(int(self.timestamp))
                self.shelf[self.counter_name][self.devname]['time'] = temptim

            else:
                tempval = self.shelf[self.counter_name][self.devname]['value']
                tempval.append(int(self.value))
                self.shelf[self.counter_name][self.devname]['value'] = tempval
                
                temptim = self.shelf[self.counter_name][self.devname]['time']
                temptim.append(int(self.timestamp))
                self.shelf[self.counter_name][self.devname]['time'] = temptim
        else:
            raise ValueError('Attempted to add more or less than 4 items as shelve record')
            return 2
  
    def get_devs(self,countname):
        """Read shelve keys, return 'Devname' ; Devname is a string identifying an entity
           to track, and update in the shelve instance"""
        return self.shelf[countname].keys()

    def read_full_value_data(self,countname,devn,maxy,maxx):
        """
        Read and return data from the shelve instance.
        This method reads only counters that represent
        full data (i.e. not rate per second)
        """
        pass

    def read_full_rate_data(self,countname,devn,maxy,maxx):
        """Read and return data from the shelve instance.
           Optimises output to write easy to plot values,
           from 0 - 100 (minimum/maximum)
           Accepts countername, device name, relative y,
           relative x (to calculate 0/100)
        """
        
        self.yplane = maxy
        self.xplane = maxx
        self.maxtimlist = list(self.shelf['timestamps'])
        if self.maxtimlist < self.xplane:
             self.skipval = 0
        else:
             self.skipval = int(round(float(len(self.maxtimlist))/self.xplane))
       #below is for 'isolated' view (first to implement)
        self.curmaxval = max(self.shelf[countname][devn]['value'])
        #self.curminval = min(self.shelf[countname][devname]['value'])
        #self.valoffset = self.curmaxval - self.curminval
        #pdb.set_trace()
        self.firstime = self.maxtimlist.index(self.shelf[countname][devn]['time'][0])
        self.lastime = self.maxtimlist.index(self.shelf[countname][devn]['time'][-1])
        if self.skipval > 0:
            self.firstindex = int(round(self.firstime/self.skipval))

        #pdb.set_trace()
        if self.skipval > 0:
            for reslice in xrange(self.firstindex,self.xplane-3,self.skipval):
                    #timeslice = self.shelf[countname][devname]['time'][reslice]
                    templist = self.shelf[countname][devn]['value'][reslice:reslice + self.skipval]
                    tempsum = sum(templist)
                    if tempsum < 1:
                        ypcent = 49
                    else:
                        avgval = int(round(tempsum / self.skipval))
                        if avgval == 1:#ugly hack.  It needs to work soon.
                            avgval = 0
                        refvalloc = int(round((avgval/self.curmaxval)*100))
                        transient_pc = float(refvalloc)/100
                        ypcent = self.yplane - int(round(self.yplane*transient_pc))
                    #if reslice > 180:
                        #pdb.set_trace()
                    if ypcent > 49:
                        ypcent = 49
                    #if ypcent == 25:
                        #pdb.set_trace()
                    yield reslice,ypcent
           
        else:
            for reslice in xrange(self.firstime,self.lastime):
                valuev = self.shelf[countname][devn]['value'][reslice]
                if valuev < 2:
                    ypcent = 51
                else :
                    refvalloc = int(round((valuev/self.curmaxval)*100))
                    transient_pc = float(refvalloc)/100
                    ypcent = self.yplane - int(round(self.yplane*transient_pc))
                yield reslice,ypcent

    def shortlist(self):
        """identify counters which have a short lifespan and
           add to a list for reference 
           Counts len of each time list and if len is less
           than the shortval, appends to list for future
           reference"""
        shortval = 20
        for i in self.shelf.keys():
            for j in self.shelf[i].keys():
                if len(s[i][j]['time']) < shortval:
                    self.shortcounts.append(j)

    def topclist(self):
        """Reads and returns list of main counters from 
           shelve"""
        return [x for x in self.shelf if x != 'timestamps']

    def shallow_ret(self):
        """Returns top and middle level data from shelve
           i.e. the main counter entry, and the dev 
           entries.  For use in display function"""
        shallow_dict = {}
#        pdb.set_trace()
        for item in self.shelf.keys():
            if item != 'timestamps':
                shallow_dict[item] = self.shelf[item].keys()#need to go deeper
        return shallow_dict

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
    def __init__(self,nslog,nsver):#countlist
        self.nslog = nslog
        self.counts = ['cc_cpu_use',
                       'nic_tot_tx_bytes',
                       'nic_tot_rx_bytes',
                       'nic_tot_rx_mbits',
                       'nic_tot_tx_mbits',
                       'vlan_tot_tx_bytes',
                       'vlan_tot_rx_bytes']
        self.totalclist = ['cc_cpu_use']
        #'mem_cur_allocsize'-implement this once I can figure out 
        #how to graph it properly

        self.metronome = ' -f sys_cur_duration_sincestart '
                #unique list for these, need special handling
                #because we look for 'totalcount' and not rate p/sec
        self.nsver = nsver
        templist = []
        #pdb.set_trace()
        for count in self.counts:
            templist.append('-f')
            templist.append(count)
        forcestring = ' '.join(templist)
        #initialise command string for subprocess
        self.command_string = 'nsconmsg' + self.nsver + ' -K ' + self.nslog + \
            ' -d current ' + forcestring + self.metronome + ' -s disptime=1' 
    
    def counter_string_to_list_with_devno(self, string):
        """Takes counter input string, modifies the timestamp and 
        returns a list representation of the string"""
        #0 = Index, 1 = rtime (relative time), 2 = totalcount-val, 
        #3 = delta, 4 = rate/sec, 5 = symbol-name 6 = &device-no, 7 = time
        totalc,ratepersec,symname,devno = 2,4,5,6 
        new_list = []
        #pdb.set_trace()
        if len(string.split()) == 11:
            new_list = string.split()[0:6]
            timelist = string.split()[6:11]#timestamp is in 4 chunks
            timestring = ' '.join(timelist[1:])#don't care about name of day
	    pattern = '%b %d %H:%M:%S %Y'
            new_list.append(int(time.mktime(time.strptime(timestring,pattern))))
            return new_list[4:]
        elif len(string.split()) == 12:
            #some special handling for differing counters
            #because some counters are in rate per second
            #and others are in 'totalcount'
            #seperating them if they are in totalclist
            templist = string.split()
            if templist[symname] in self.totalclist:#symbol name in clist
                new_list.append(templist[totalc])
                new_list.append(templist[symname])
                new_list.append(templist[devno])
            else:
                new_list.append(templist[ratepersec])
                new_list.append(templist[symname])
                new_list.append(templist[devno])
            timelist = string.split()[7:12]
            timestring = ' '.join(timelist[1:])
	    pattern = '%b %d %H:%M:%S %Y'
            new_list.append(int(time.mktime(time.strptime(timestring,pattern))))
            return new_list
        else:
            pass

    def nratechecker(self):
        """Netscaler specific log reading method.  References
        counter_string_to_list_with_devno()
        """
        # regexes for input handling
        detect_log_headers = re.compile('(reltime)|(Index)|(Performance)|(performance)|(Build)')
        strip_path_newnslog = re.compile('newnslo\S+')
        # locate log file
        input_file = os.path.join(os.getcwd(), self.nslog)
        if not os.path.exists(input_file):
            raise IOError('Input file not found')

        #parse variables into list - because it is a bytestream passed 
        #from subprocess need to use splitlines()

        for line in subprocess.check_output([self.command_string], 
                shell=True).splitlines():
            if not detect_log_headers.search(line):
                if line.strip():#make sure the line is _not_ empty
                    outstring = self.counter_string_to_list_with_devno(line)
                    yield outstring

