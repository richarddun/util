#!/usr/bin/env python2
"""Window writing and updating in curses"""

import curses
from curses import panel
import time

class BaseWin(object):
    """
    Instantiates and handles movement and selection within the
    curses canvas.  Takes height (h) and width (w) of terminal
    as arguments
    """
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
        """
        Handles movement within the 'base' counter selection screen.
        Counter selection is read from a datahandler method passed to 
        this method by the main constellation program.

        Takes a list of strings - counter names (from datahandler), 
        and a dict with counter:dev (e.g. - 'nic_rx':'eth0') as arguments
        """
        self.context = 1 #initial selection context
        self.mlocptr = 1 #track index (current)
        self.prevloc = 1 #track index (previous)
        self.s_curloc = 1 #track index (subwin current)
        self.s_prevloc = 1 #track index (subwin previous)
        self.maxstrlen = 0
        self.pan_selectref = {}
        self.upperclist = topclist #main list of counters
        self.countmap = countermap #dict containing counter:devs
        self.mlocationref = {} 
        self.subwinls = [] #sub window list
        self.subpans = {} #sub panels dict
        self.rightshift = 1
        self.writeoffset =1
        self.paneldevlist = []
        self.win.addstr(self.starty,self.startx,
                'Please select a base counter:')
        for countl in self.upperclist:
            if len(countl) > self.maxstrlen:
                self.maxstrlen = len(countl)
                #get longest stringlen from list
        for counter in self.countmap:
            for dev in counter:
                self.maxdevstrlen = len(dev)
        for index,counter in enumerate(self.upperclist,2):
            self.subwinls.append(curses.newwin(self.len_y-index,80,index,35)) 
            #create new window, y - index (increments)
            #x - longest string, then append to list
            self.subpans[counter] = curses.panel.new_panel(self.subwinls[index-2])
            #index minus 2 because I'm drawing positions on screen as well as 
            #indexing into a list
            for dev in self.countmap[counter]:
                curY = self.writeoffset
                self.paneldevlist.append(dev)
                if curY + 5 > self.len_y-index:
                    self.rightshift += 50
                    self.writeoffset = 1
                self.subwinls[index-2].border('|','|','-','-','+','+','+','+')
                self.subwinls[index-2].addstr(self.writeoffset,self.rightshift,dev)
                #remember where we write all strings
            	if counter in self.pan_selectref:
		    self.pan_selectref[counter].update(
		     {dev:
		     {'locationy':self.writeoffset,
		      'locationx':self.rightshift,
		      'selected':False}})
		else:
		    self.pan_selectref.update(
		     {counter:
		     {dev:
		     {'locationy':self.writeoffset,
	   	      'locationx':self.rightshift,
		      'selected':False}}})
                self.writeoffset += 1 #shameless abandonment of enumerate
            self.subpans[counter].set_userptr(self.paneldevlist)
            self.writeoffset = 1
            self.paneldevlist = []

        for index,countl in enumerate(self.upperclist,1):
            self.mlocationref[index]=countl #remember for later
            if index == 1:
                self.win.addstr(self.starty+index,self.startx,countl,
                    curses.A_REVERSE)
            else:
                self.win.addstr(self.starty+index,self.startx,countl)
        self.win.refresh()
        

    def m_selectdown(self):
        """
        Method to 'highlight' the next counter name when the down
        arrow key is pressed.  Next counter is rewritten with reverse
        video, previous counter is re-written without.
        Corresponding Panel containing devs is brought to top().
        """
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
            self.subpans[self.mlocationref[self.mlocptr]].top()
            self.prevloc = self.mlocptr
        else:
            self.mlocptr += 1
            self.win.addstr(self.starty+self.mlocptr,self.startx,
                self.mlocationref[self.mlocptr],curses.A_REVERSE)
            self.win.addstr(self.starty+self.prevloc,self.startx,
                self.mlocationref[self.prevloc])
            self.prevloc = self.mlocptr
            self.subpans[self.mlocationref[self.mlocptr]].top()

        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()
    
    def m_selectup(self):
        """
        Method to 'highlight' the next counter name when the up
        arrow key is pressed.  Next counter is rewritten with reverse
        video, previous counter is re-written without.
        Corresponding Panel containing devs is brought to top().
        """
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
            self.subpans[self.mlocationref[self.mlocptr]].top()
            self.prevloc = self.mlocptr 
        else:
            self.mlocptr -= 1
            self.win.addstr(self.starty+self.mlocptr,self.startx,
                self.mlocationref[self.mlocptr],curses.A_REVERSE)
            self.win.addstr(self.starty+self.prevloc,self.startx,
                self.mlocationref[self.prevloc])
            self.prevloc = self.mlocptr
            self.subpans[self.mlocationref[self.mlocptr]].top()

        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()

    def s_selectdown(self):
        if self.s_curloc + 2 > len(self.curdevlist):
            self.s_curloc = 0
            y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationy']
            x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationx']
            self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,
                    self.curdevlist[self.s_curloc],curses.A_REVERSE)
            y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationy']
            x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationx']
            self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_prevloc])
            self.s_prevloc = self.s_curloc

        else: 
            self.s_curloc += 1
            y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationy']
            x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationx']
            self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,
                    self.curdevlist[self.s_curloc],curses.A_REVERSE)
            y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationy']
            x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationx']
            self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_prevloc])
            self.s_prevloc = self.s_curloc
        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()
       

    def s_selectup(self):
        if self.s_curloc - 1 < 0:
            self.s_curloc = len(self.curdevlist) - 1
            y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationy']
            x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationx']
            self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,
                    self.curdevlist[self.s_curloc],curses.A_REVERSE)
            y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationy']
            x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationx']
            self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_prevloc])
            self.s_prevloc = self.s_curloc

        else: 
            self.s_curloc -= 1
            y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationy']
            x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationx']
            self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,
                    self.curdevlist[self.s_curloc],curses.A_REVERSE)
            y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationy']
            x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationx']
            self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_prevloc])
            self.s_prevloc = self.s_curloc
        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()



    def p_jump(self):
        self.curdevlist = self.subpans[self.mlocationref[self.mlocptr]].userptr()
        self.s_curloc = 0
        self.s_prevloc = 0
        #retrieve x and y coords from previously built dict
        #using indexing pointers from m_select methods
        y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[0]]['locationy']
        x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[0]]['locationx']
        self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,
                self.curdevlist[0],curses.A_REVERSE)
        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()

    def m_jump(self):
        #TODO - Clear last reversed video string when jumping back to main cselect
        pass

        #TODO - add counter selection method, initialise color pair or embolden



