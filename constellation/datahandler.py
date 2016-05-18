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
        self.sdict = {}
        self.hitmax = False
        self.hitmin = False
        self.offset = 0
        self.drawtrack = {}

    def add_data(self,buf):
        """Add data passed from list containing specific values to a shelve record
           Values expected : 0 - Value (int),1 - Name (str), 2 - Dev_name (str), 
           3 - Timestamp (int)
           Also note max/min val/time while reading data
        """
        tempval = []
        temptim = []
        if buf[1] == 'sys_cur_duration_sincestart':
            if 'timestamps' in self.sdict.keys():
                self.sdict['timestamps'].append(buf[2])
            else:
                self.sdict['timestamps'] = []
                
                self.sdict['timestamps'].append(buf[2])
        elif len(buf) == 4:
            self.value = buf[0]
            self.counter_name = buf[1]
            self.devname = buf[2]
            self.timestamp = buf[3]
            #take a note of max/min of time/values for later
            if not self.counter_name in self.sdict:
                self.sdict[self.counter_name] = {self.devname:{'value':[],'time':[]}}
                self.sdict[self.counter_name][self.devname]['value'].append(int(self.value))
                self.sdict[self.counter_name][self.devname]['time'].append(int(self.timestamp))
                self.drawtrack[self.counter_name] = {self.devname:{'overallen':1,'offset':0}}

            if not self.devname in self.sdict[self.counter_name]:
                self.sdict[self.counter_name].update({self.devname:{'value':[],'time':[]}})
                self.sdict[self.counter_name][self.devname]['value'].append(int(self.value))
                self.sdict[self.counter_name][self.devname]['time'].append(int(self.timestamp))
                self.drawtrack[self.counter_name].update({self.devname:{'overallen':1,'offset':0}})

            else:
                self.sdict[self.counter_name][self.devname]['value'].append(int(self.value))
                self.sdict[self.counter_name][self.devname]['time'].append(int(self.timestamp))
                self.drawtrack[self.counter_name][self.devname]['overallen']+=1
        else:
            raise ValueError('Attempted to add more or less than 4 items as shelve record')
            return 2
  
    def get_devs(self,countname):
        """Read shelve keys, return 'Devname' ; Devname is a string identifying an entity
           to track, and update in the shelve instance"""
        return self.sdict[countname].keys()

    def resetcounters(self):
        delattr(self,'maxrate')
        delattr(self,'minrate')
        delattr(self,'spanrate')
        delattr(self,'maxmindict')

    def fillmaxminvals(self,countname,dev):
        curmax = max(self.sdict[countname][dev]['value'])
        curmin = min(self.sdict[countname][dev]['value'])
        if not hasattr(self, 'maxrate'):
            self.maxrate = curmax
            self.minrate = curmin
            self.spanrate = self.maxrate - self.minrate
            self.maxmindict = {countname:{'maxrate':self.maxrate,'minrate':self.minrate,'spanrate':self.spanrate}}
        else:
            if self.maxrate < curmax:
                self.maxrate = curmax
                self.hitmax = True
            if self.minrate > curmin:
                self.minrate = curmin
                self.hitmin = True
            if self.hitmax or self.hitmin:
                self.spanrate = self.maxrate - self.minrate
                self.maxmindict[countname] = {'maxrate':self.maxrate,
                    'minrate':self.minrate,'spanrate':self.spanrate}
                self.hitmax,self.hitmin = False,False

    def prep_data(self,maxy,maxx):
        """
        prepare some variables that I can't initialise
        anywhere else (without a non-trivial redesign)
        """
        self.maxtimlist = list(self.sdict['timestamps'])
        self.yplane = maxy
        self.xplane = maxx
        self.lastime = len(self.maxtimlist) - 1

    def read_full_rate_data(self,countname,devn,offset=None):
        """Read and return data
           Optimises output to write easy to plot values,
           from 0 - 100 (minimum/maximum)
           Accepts countername, device name, relative y,
           relative x (to calculate 0/100)
        """
        
        
        if offset == None:
            self.firstime = self.maxtimlist.index(self.sdict[countname][devn]['time'][0])
        else: 
            self.firstime = offset
            #pdb.set_trace()
        for reslice in xrange(self.firstime,self.drawtrack[countname][devn]['overallen']):
            #try:
            valuev = self.sdict[countname][devn]['value'][reslice]
            #except:
            #    continue
            #if valuev < 2:
            #    ypcent = 49
            #else :

            if countname == 'cc_cpu_use':
                transient_pc = valuev/100     
            
            else:
                refvalloc = int(round((valuev/self.spanrate)*100))
                transient_pc = float(refvalloc)/100
            ypcent = self.yplane - int(round(self.yplane*transient_pc))
            if ypcent > 49:
                ypcent = 49
            yield reslice,ypcent

    def topclist(self):
        """Reads and returns list of main counters from 
           shelve"""
        templist = []
        for x in self.sdict:
            if x == 'timestamps':
                continue
            templist.append(x)
        
        return templist

    def shallow_ret(self):
        """Returns top and middle level data from shelve
           i.e. the main counter entry, and the dev 
           entries.  For use in display function"""
        shallow_dict = {}
        for item in self.sdict.keys():
            if item != 'timestamps':
                shallow_dict[item] = self.sdict[item].keys()#need to go deeper
        return shallow_dict

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

