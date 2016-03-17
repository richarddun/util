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
        
    def Main_Cselect(self,topclist):
        self.context = 1 #initial selection context
        self.mlocptr = 1 #track index (current)
        self.prevloc = 1 #track index (previous)
        self.maxstrlen = 0
        self.upperclist = topclist
        self.mlocationref = {}
        for cl in self.upperclist:
            if len(cl) > self.maxstrlen:
                self.maxstrlen = len(cl)#get longest stringlen from list
        for index,cl in enumerate(self.upperclist,1):
            self.mlocationref[index]=cl #remember for later
            if index == 1:
                self.win.addstr(self.starty+index,self.startx,cl,
                    curses.A_REVERSE)
            else:
                self.win.addstr(self.starty+index,self.startx,cl)
        self.win.refresh()

    def selectdown(self):
        if self.mlocptr + 1 > len(self.mlocationref.keys()):
        #if pressing down will send us off the bottom
        #go back to the top
            self.prevloc = self.mlocptr
            self.win.addstr(self.starty+self.prevloc,self.startx,
                self.mlocationref[self.prevloc])
            #unset the vid reverse on previous string
            self.mlocptr = 1
            self.win.addstr(self.starty+self.mlocptr,self.startx,
                self.mlocationref[self.mlocptr],curses.A_REVERSE)
            #invert the text to highlight current selection
        else:
            self.mlocptr += 1
            self.win.addstr(self.starty+self.mlocptr,self.startx,
                self.mlocationref[self.mlocptr],curses.A_REVERSE)
            self.win.addstr(self.starty+self.prevloc,self.startx,
                self.mlocationref[self.prevloc])
            self.prevloc = self.mlocptr
        self.win.refresh()

    def selectup(self):
        if (self.mlocptr - 1) < 1:
        #if pressing up will send us off the top
        #go back to the bottom
            self.prevloc = self.mlocptr
            self.win.addstr(self.starty+self.prevloc,self.startx,
                self.mlocationref[self.prevloc])
            #unset the vid reverse on previous string
            self.mlocptr = len(self.mlocationref.keys())
            self.win.addstr(self.starty+self.mlocptr,self.startx,
                self.mlocationref[self.mlocptr],curses.A_REVERSE)
            #invert the text to highlight current selection
        else:
            self.mlocptr -= 1
            self.win.addstr(self.starty+self.mlocptr,self.startx,
                self.mlocationref[self.mlocptr],curses.A_REVERSE)
            self.win.addstr(self.starty+self.prevloc,self.startx,
                self.mlocationref[self.prevloc])
            self.prevloc = self.mlocptr
       

    def Sub_Cselect(self):
        pass





