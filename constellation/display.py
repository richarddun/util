#!/usr/bin/env python2
"""Window writing and updating in curses"""

import curses
from curses import panel
from collections import OrderedDict
import time
import os 

class BaseWin(object):
    """
    Instantiates and handles movement and selection within the
    curses canvas.  Takes height (h) and width (w) of terminal
    as arguments
    """
    def __init__(self,h,w):
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_RED)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_RED)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)
        #now init color pairs for counter drawing, black bg
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(9, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(11, curses.COLOR_CYAN, curses.COLOR_BLACK)
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
        self.context = 1 #initial selection context
        self.mlocptr = 1 #track index (current)
        self.prevloc = 1 #track index (previous)
        self.s_curloc = 1 #track index (subwin current)
        self.s_prevloc = 1 #track index (subwin previous)
        self.maxstrlen = 0
        self.pan_selectref = OrderedDict({})
        self.panmvloc = 0
        self.toggledev = []
        self.introdone = False

    def Intro_Option_draw(self):
        self.gwin_ylen = self.len_y/3
        self.gwin_xlen = self.len_x/3
        self.gwin = curses.newwin(self.len_y/4,(self.len_x/2-self.gwin_xlen/2),self.gwin_ylen,self.gwin_xlen)
        self.gwin.border('|','|','-','-','+','+','+','+')
        self.gpan = curses.panel.new_panel(self.gwin)
        self.gprod = '**NSCONSTELLATION**'
 #       self.goption = ['-Isolated-','-Comparison-']
 #       self.gtext = ['View counters for each device in an isolated window','View selected counters simultaneously in one window']
        self.gwin.addstr(1, self.gwin_xlen/2 - (len(self.gprod)/2),self.gprod,curses.color_pair(3))
#        self.gwin.addstr(3, self.gwin_xlen/4, self.goption[0], curses.A_REVERSE)
#        self.gwin.addstr(3, (self.gwin_xlen/4)*3, self.goption[1])
#        self.gwin.addstr(7, 4,self.gtext[0])
#        self.isoloc = [3,self.gwin_xlen/4]
#        self.conloc = [3,((self.gwin_xlen/4)*3)]
#        self.incurselect = 0
#below the stripped down version (for now)
        self.gwin.addstr(3, self.gwin_xlen/5, 'Rate count visualiser')
        self.gwin.addstr(5, self.gwin_xlen/5, 'Shift and q to quit')
        self.gwin.addstr(6, self.gwin_xlen/5, 'Shift and h for  contextual help')
        self.gwin.addstr(8, self.gwin_xlen/5, 'Press Spacebar to continue')
        self.gpan.top()
        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()

#    def Intro_option_move(self):
#        if self.incurselect == 0:
#            self.gwin.addstr(3, self.gwin_xlen/4, self.goption[0])
#            self.gwin.addstr(3, (self.gwin_xlen/4)*3, self.goption[1],curses.A_REVERSE)
#            self.gwin.addstr(5,1,' '*len(self.gtext[0]))
#            self.gwin.addstr(7,4,self.gtext[1])
#            self.incurselect = 1
#        elif self.incurselect == 1:
#            self.gwin.addstr(3, self.gwin_xlen/4, self.goption[0],curses.A_REVERSE)
#            self.gwin.addstr(3, (self.gwin_xlen/4)*3, self.goption[1])
#            self.gwin.addstr(5,1,' '*len(self.gtext[1]))
#            self.gwin.addstr(7,4,self.gtext[0])
#            self.incurselect = 0
#        curses.panel.update_panels()
#        curses.doupdate()
#        self.win.refresh()
               
    def Intro_option_select(self):
#        if self.incurselect == 0:
#            self.gwin.addstr(3, self.gwin_xlen/4, self.goption[0],curses.color_pair(4))
#        else:
#            self.gwin.addstr(3, (self.gwin_xlen/4)*3, self.goption[1], curses.color_pair(4))
#        curses.panel.update_panels()
#        curses.doupdate()
#        self.win.refresh()
#        time.sleep(.5)
        self.introdone = True
        self.gpan.hide()

    def Selection_Warn_Draw(self):
        self.g1text = 'Maximum selection is 8 unique counters.  To continue '
        self.g2text = 'de-select a previous counter'
        self.extext = 'Press Space to continue'
        self.warnwin_ylen = self.len_y/3
        self.warnwin_xlen = self.len_x/3
        self.warnwin = curses.newwin(6,len(self.g1text)+3,self.len_y/2,(self.len_x/2) - (len(self.g1text)/2))
        self.warnwin.border('|','|','-','-','+','+','+','+')
        self.warnpan = curses.panel.new_panel(self.warnwin)
        self.warnwin.addstr(2,1,self.g1text)
        self.warnwin.addstr(3,1,self.g2text)
        self.warnwin.addstr(4,(len(self.g1text)-len(self.extext)),self.extext)
        self.warnpan.top()
        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()

    def Selection_Warn_Dismiss(self):
        self.warning = False
        self.warnpan.hide()
        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()

    def Help_Draw(self):
        self.helptextlist = []
        self.helpstring = ' '
        self.toplen = 0
        with open('help.txt','r') as helpfile:
            for line in helpfile:
                self.helptextlist.append(line)
                if len(line) > self.toplen:
                    self.toplen = len(line)
        self.helpwin_ylen = len(self.helptextlist) + 2
        self.helpwin_xlen = self.toplen + 4 
        self.helpwin = curses.newwin(self.helpwin_ylen,self.helpwin_xlen,
                self.len_y/2-(len(self.helptextlist)/2),
                (self.len_x/2)-(self.toplen/2)+3)
        self.helppan = curses.panel.new_panel(self.helpwin)
        for index,line in enumerate(self.helptextlist,1):
            self.helpstring = self.helptextlist[index-1]
            self.helpwin.addstr(index,1,self.helptextlist[index-1])
        self.helpwin.border('|','|','-','-','+','+','+','+')
        self.helppan.top()
        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()

    def Help_Dismiss(self):
        self.showing_help = False
        self.helppan.hide()
        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()

    def Main_Cselect(self,topclist,countermap):
        """
        Handles movement within the 'base' counter selection screen.
        Counter selection is read from a datahandler method passed to 
        this method by the main constellation program.

        Takes a list of strings - counter names (from datahandler), 
        and a dict with counter:dev (e.g. - 'nic_rx':'eth0') as arguments
        """
        self.upperclist = topclist #main list of counters
        self.countmap = countermap #dict containing counter:devs
        self.mlocationref = OrderedDict({}) 
        self.subwinls = [] #sub window list
        self.subpans = OrderedDict({}) #sub panels dict
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
                    self.rightshift += 40
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
        self.subpans[self.mlocationref[self.mlocptr]].top()
        curses.panel.update_panels()
        curses.doupdate()
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
        """
        Method to 'highlight' the next device name when the down
        arrow key is pressed.  Next device string is rewritten
        with reverse video, previous device is re-written without.
        """
        if (self.s_curloc + 2 > len(self.curdevlist)) and (len(self.curdevlist) > 1):
            self.s_curloc = 0
            if not (self.mlocationref[self.mlocptr],self.curdevlist[self.s_curloc]) in self.toggledev:
                y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationy']
                x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationx']
                self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_curloc],curses.A_REVERSE)
            elif (self.mlocationref[self.mlocptr],self.curdevlist[self.s_curloc]) in self.toggledev:
                y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationy']
                x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationx']
                self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_curloc],curses.color_pair(2))
            if not (self.mlocationref[self.mlocptr],self.curdevlist[self.s_prevloc]) in self.toggledev:
                y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationy']
                x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationx']
                self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_prevloc])
            elif (self.mlocationref[self.mlocptr],self.curdevlist[self.s_prevloc]) in self.toggledev:
                y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationy']
                x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationx']
                self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_prevloc],curses.color_pair(1))

            self.s_prevloc = self.s_curloc

        elif len(self.curdevlist) > 1: 
            self.s_curloc += 1
            if not (self.mlocationref[self.mlocptr],self.curdevlist[self.s_curloc])in self.toggledev:
                y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationy']
                x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationx']
                self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_curloc],curses.A_REVERSE)
            elif (self.mlocationref[self.mlocptr],self.curdevlist[self.s_curloc]) in self.toggledev:
                y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationy']
                x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationx']
                self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_curloc],curses.color_pair(2))
           
            if not (self.mlocationref[self.mlocptr],self.curdevlist[self.s_prevloc]) in self.toggledev:
                y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationy']
                x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationx']
                self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_prevloc])
            elif (self.mlocationref[self.mlocptr],self.curdevlist[self.s_prevloc]) in self.toggledev:
                y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationy']
                x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationx']
                self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_prevloc],curses.color_pair(1))
        
            self.s_prevloc = self.s_curloc
        else:
            self.s_prevloc = self.s_curloc
        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()
       

    def s_selectup(self):
        """
        Method to 'highlight' the previous device name when the up
        arrow key is pressed.  Previous device string is rewritten
        with reverse video, next device string is re-written without.
        """
        if (self.s_curloc - 1 < 0) and (len(self.curdevlist) > 1):
            self.s_curloc = len(self.curdevlist) - 1
            if not (self.mlocationref[self.mlocptr],self.curdevlist[self.s_curloc])  in self.toggledev:
                y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationy']
                x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationx']
                self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_curloc],curses.A_REVERSE)
            elif (self.mlocationref[self.mlocptr],self.curdevlist[self.s_curloc]) in self.toggledev:
                y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationy']
                x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationx']
                self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_curloc],curses.color_pair(2))

            if not (self.mlocationref[self.mlocptr],self.curdevlist[self.s_prevloc]) in self.toggledev:
                y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationy']
                x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationx']
                self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_prevloc])
            elif (self.mlocationref[self.mlocptr],self.curdevlist[self.s_prevloc]) in self.toggledev:
                y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationy']
                x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationx']
                self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_prevloc],curses.color_pair(1))

            self.s_prevloc = self.s_curloc

        elif (len(self.curdevlist) > 1):
            self.s_curloc -= 1
            if not (self.mlocationref[self.mlocptr],self.curdevlist[self.s_curloc]) in self.toggledev:
                y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationy']
                x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationx']
                self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_curloc],curses.A_REVERSE)
            elif (self.mlocationref[self.mlocptr],self.curdevlist[self.s_curloc]) in self.toggledev:
                y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationy']
                x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_curloc]]['locationx']
                self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_curloc],curses.color_pair(2))

            if not (self.mlocationref[self.mlocptr],self.curdevlist[self.s_prevloc]) in self.toggledev:
                y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationy']
                x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationx']
                self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_prevloc])
            elif (self.mlocationref[self.mlocptr],self.curdevlist[self.s_prevloc]) in self.toggledev:
                y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationy']
                x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationx']
                self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_prevloc],curses.color_pair(1))

            self.s_prevloc = self.s_curloc
        else:
            self.s_prevloc = self.s_curloc
        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()

    def p_jump(self):
        """
        Method to 'jump' to the currently selected panel, and highlight
        the first available dev string with reverse video
        """
        self.win.addstr(self.starty+self.mlocptr,self.startx,self.mlocationref[self.mlocptr])       
        self.curdevlist = self.subpans[self.mlocationref[self.mlocptr]].userptr()
        self.s_curloc = 0
        self.s_prevloc = 0
        #retrieve x and y coords from previously built dict
        #using indexing pointers from m_select methods
        if not (self.mlocationref[self.mlocptr],self.curdevlist[self.s_curloc]) in self.toggledev:
            y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[0]]['locationy']
            x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[0]]['locationx']
            self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[0],curses.A_REVERSE)
        elif (self.mlocationref[self.mlocptr],self.curdevlist[self.s_curloc]) in self.toggledev:
            y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[0]]['locationy']
            x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[0]]['locationx']
            self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_curloc],curses.color_pair(2))

        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()

    def m_jump(self):
        """
        Method to 'jump' back to the main counter selection window,
        clearing the previously highlighted string
        """
        self.win.addstr(self.starty+self.mlocptr,self.startx,self.mlocationref[self.mlocptr],curses.A_REVERSE)       
        #Clear last reversed video string when jumping back to main cselect
        if not (self.mlocationref[self.mlocptr],self.curdevlist[self.s_curloc]) in self.toggledev:
            y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationy']
            x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationx']
            self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_prevloc])
        elif (self.mlocationref[self.mlocptr],self.curdevlist[self.s_curloc]) in self.toggledev:
            y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationy']
            x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationx']
            self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_curloc],curses.color_pair(1))
        self.s_prevloc = self.s_curloc
        self.context = 1
        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()

    def dev_toggle(self):
        """
        Method to highlight and track each dev selected in each panel (counter)
        """
        if not (self.mlocationref[self.mlocptr],self.curdevlist[self.s_curloc]) in self.toggledev:
            self.toggledev.append((self.mlocationref[self.mlocptr],self.curdevlist[self.s_curloc]))
            y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationy']
            x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationx']
            self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_prevloc],curses.color_pair(1))
        else:
            self.toggledev.remove((self.mlocationref[self.mlocptr],self.curdevlist[self.s_curloc]))
            y_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationy']
            x_coord = self.pan_selectref[self.mlocationref[self.mlocptr]][self.curdevlist[self.s_prevloc]]['locationx']
            self.subwinls[self.mlocptr-1].addstr(y_coord,x_coord,self.curdevlist[self.s_prevloc],curses.A_REVERSE)
        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()

    def on_toggled(self):
        if (self.mlocationref[self.mlocptr],self.curdevlist[self.s_curloc]) in self.toggledev:
            return True
        else:
            return False

    def generate_graphPanels(self):
        """
        Method to read the current toggledev list of tuples and build
        a dict with the values.  This makes it easier to iterate 
        intelligently through the values, and build a window for each
        unique counter.
        
        Format of the dict is :

        counterplotdict = {counter:[dev,dev,dev,dev],counter:[dev,dev,dev]}
        """
        self.graphwinsl = []
        self.graphpansd = OrderedDict({})
        self.gwlegendsl = []
        self.gplegendsd = OrderedDict({})
        self.countplotdict = OrderedDict({})
        counter,dev = 0,1
        for entry in self.toggledev:
            if entry[counter] in self.countplotdict:
                self.countplotdict[entry[counter]].append(entry[dev])
            else:
                self.countplotdict[entry[counter]] = [entry[dev]]
        for index,entry in enumerate(self.countplotdict):
            self.graphwinsl.append(curses.newwin(self.len_y,self.len_x,0,0))
            self.graphpansd[entry] = curses.panel.new_panel(self.graphwinsl[index])
            self.gwlegendsl.append(curses.newwin(8,self.len_x/4,2,2))
            self.gplegendsd[entry] = curses.panel.new_panel(self.gwlegendsl[index])

            self.gwlegendsl[index].addstr(1,1,entry)
        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()
    
    def hide_graphPanels(self):
        for panel in self.graphpansd:
            self.graphpansd[panel].hide()
        for panel in self.gplegendsd:
            self.gplegendsd[panel].hide()
        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()

    def addname(self,device,ystrindex,windex):
        self.gwlegendsl[windex].addstr(ystrindex+3,1,device,curses.color_pair(5+ystrindex))

    def spray_dots(self,y,x,num,color):
        """
        Method to draw a '*' at a given y location, at 'num' window.
        """
        self.graphchars = ['*','#','@','&','^','"','!','~']
        try: 
            self.graphwinsl[num].addch(y,x,'*',curses.color_pair(5+color))
        
            for line in xrange(y+1,self.len_y):
                self.graphwinsl[num].addch(line,x,'|',curses.color_pair(5+color))
        except:
            pass
        curses.panel.update_panels()
        curses.doupdate()

    def clear_win(self,num):
        self.graphwinsl[self.panmvloc].clear()
        curses.panel.update_panels()
        curses.doupdate()
        self.graphwinsl[self.panmvloc].refresh()

    def toggle_legend(self):
        if hasattr(self,'legendshow'):
            for index,pan in enumerate(self.gplegendsd):
                if index == self.panmvloc:
                    self.gplegendsd[pan].top()
            delattr(self,'legendshow')
        else:
            self.legendshow = True
            for index,pan in enumerate(self.gplegendsd):
                #if index == self.panmvloc:
                #    pass
                self.gplegendsd[pan].hide()
        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()

    def graphshow(self,move):
        if len(self.graphpansd.keys()) == 1:
            pass
        else:
            self.panmvloc += move
            if self.panmvloc < 0:
                self.panmvloc = len(self.graphpansd.keys()) - 1
            if self.panmvloc > len(self.graphpansd.keys()) - 1:
                self.panmvloc = 0
            pan = self.graphpansd.keys()[self.panmvloc]
            self.graphpansd[pan].top()
            pan = self.gplegendsd.keys()[self.panmvloc]
            self.gplegendsd[pan].top()
        curses.panel.update_panels()
        curses.doupdate()
        self.graphwinsl[self.panmvloc].refresh()


    def one_refresh(self,num):
        self.graphwinsl[num].refresh()

    def refresh(self):
        curses.panel.update_panels()
        curses.doupdate()
        self.win.refresh()





