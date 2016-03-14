#!/usr/bin/env python2
"""Window writing and updating in curses"""

import curses
import time

class CselectWin(object):
    def __init__(self,h,w):
        self.starty, self.startx = 0,0
        self.len_y,self.len_x = h,w
        self.win = curses.newwin(self.len_y,self.len_x,self.starty,self.startx)

    def Draw_main_cselect(self,topclist):
        self.maxstrlen = 0
        self.upperclist = topclist
        for cl in self.upperclist:
            if len(cl) > self.maxstrlen:
                self.maxstrlen = len(cl)#get longest stringlen from list
        for index,cl in enumerate(self.upperclist):
            self.win.addstr(self.starty+index,self.startx,cl)
        self.win.refresh()   
            

