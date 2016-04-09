#!/usr/bin/env python2
"""Window writing and updating in curses"""

import curses
from curses import panel
import time

class BaseWin(object):
    def __init__(self,h,w):
        self.starty, self.startx = 1,1
        self.len_y,self.len_x = h,w
        self.win = curses.newwin(self.len_y,self.len_x,self.starty,self.startx)
        self.infob_h = int(round(self.len_y * .15))
        self.infob_offset = self.len_y - self.infob_h 
        #offset is size of info box minus length of y axis
        self.infobox = curses.newwin(self.infob_h,self.len_x,self.infob_offset,
            self.startx)
        self.infobox.border('|','|','-','-','+','+','+','+')

        self.countpan = curses.panel.new_panel(self.win)
        self.infobpan = curses.panel.new_panel(self.infobox)
        self.infobpan.hide()#hiding it for now

    def Main_Cselect(self,topclist,countermap):
        self.context = 1 #initial selection context
        self.mlocptr = 1 #track index (current)
        self.prevloc = 1 #track index (previous)
        self.maxstrlen = 0
        self.upperclist = topclist #main list of counters
        self.countmap = countermap #dict containing counter:devs
        self.mlocationref = {} 
        self.subwinmap = {} #dict containing panels for devs
        self.subpans = []
        self.win.addstr(self.starty,self.startx,
                'Please select a base counter:')
        for countl in self.upperclist:
            if len(countl) > self.maxstrlen:
                self.maxstrlen = len(countl)
                #get longest stringlen from list
        
        for index,countl in enumerate(self.upperclist,1):
            self.mlocationref[index]=countl #remember for later
            if index == 1:
                self.win.addstr(self.starty+index,self.startx,countl,
                    curses.A_REVERSE)
            else:
                self.win.addstr(self.starty+index,self.startx,countl)
        self.win.refresh()
        

    def selectdown(self):
        rightshift = 0
        if self.mlocptr + 1 > len(self.mlocationref.keys()):
        #if pressing down will send us off the bottom
        #go back to the top
            self.win.addstr(self.starty+self.prevloc,self.startx,
                self.mlocationref[self.prevloc])
            #unset the vid reverse on previous string
            self.mlocptr = 1
            self.win.addstr(self.starty+self.mlocptr,self.startx,
                self.mlocationref[self.mlocptr],curses.A_REVERSE)
            #invert the text to highlight current selection
           
            self.prevloc = self.mlocptr
        else:
            self.mlocptr += 1
            self.win.addstr(self.starty+self.mlocptr,self.startx,
                self.mlocationref[self.mlocptr],curses.A_REVERSE)
            index = 1
            for counter in self.countmap[
                           self.mlocationref[
                           self.mlocptr]]:#need to go deeper
            #for posterity, line 66 and below : 
            #self.countmap is a dict passed to the class method, plucked
            #from datahandler module (shallow_ret() method).  It is a 
            #dict containing counter:devname only (not filled with 
            #actual counter data like rate/time).  self.mlocationref is 
            #another dict, containing counter name and index (where 
            #drawn on the y axis), and self.mlocptr is incremented or
            #decremented based on whether up or down is pressed (via 
            #selectdown() or selectup() methods. Basically these lines
            #of code write a 'submenu' of 'devs' for each 'counter' that
            #is redrawn each time an up or down key is pressed.
                curY = (self.starty+self.prevloc+index)
                if curY + 3 > self.len_y:
                    rightshift += 30
                    index = 1
                self.win.addstr(self.starty+self.prevloc+index,self.startx+self.maxstrlen+rightshift+3,counter)
                index += 1
            self.win.addstr(self.starty+self.prevloc,self.startx,
                self.mlocationref[self.prevloc])
            self.prevloc = self.mlocptr
        
        self.win.refresh()
        
    def selectup(self):
        if (self.mlocptr - 1) < 1:
        #if pressing up will send us off the top
        #go back to the bottom
            self.win.addstr(self.starty+self.prevloc,self.startx,
                self.mlocationref[self.prevloc])
            #unset the vid reverse on previous string
            self.mlocptr = len(self.mlocationref.keys())
            self.win.addstr(self.starty+self.mlocptr,self.startx,
                self.mlocationref[self.mlocptr],curses.A_REVERSE)
            #invert the text to highlight current selection
            self.prevloc = self.mlocptr
        else:
            self.mlocptr -= 1
            self.win.addstr(self.starty+self.mlocptr,self.startx,
                self.mlocationref[self.mlocptr],curses.A_REVERSE)
            self.win.addstr(self.starty+self.prevloc,self.startx,
                self.mlocationref[self.prevloc])
            self.prevloc = self.mlocptr
        self.win.refresh()

    def Sub_Cselect(self,countname):
        pass


