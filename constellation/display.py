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
        self.infob_h = int(round(self.len_y * .15)
        self.infob_offset = self.len_y - self.infob_h 
        #offset is size of info box minus length of y axis
        self.infobox = curses.newwin(self.infob_h,self.len_x,self.infob_offset,
            self.startx)
        self.infobox.border('|','|','-','-','+','+','+','+')

        self.countpan = curses.panel.new_panel(self.win)
        self.infobpan = curses.panel.new_panel(self.infobox)
        
    def Draw_main_cselect(self,topclist):
        self.maxstrlen = 0
        self.upperclist = topclist
        for cl in self.upperclist:
            if len(cl) > self.maxstrlen:
                self.maxstrlen = len(cl)#get longest stringlen from list
        for index,cl in enumerate(self.upperclist):
            self.win.addstr(self.starty+index,self.startx,cl)
        #self.win.refresh()



