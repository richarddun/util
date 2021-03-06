#!/usr/bin/env python2
"""Main program control and logic

Richard Dunne, 2016

Graph rate values from a given newnslog.

"""

import argparse
import os
import sys
import subprocess
import re
import curses
import time
from datahandler import *
from display import *

def check_args():
    """
    argparse to validate input to program
    """
    global ver,logfile
    parser = argparse.ArgumentParser(description ='Rate count visualiser')
    group1 = parser.add_argument_group('required arguments')
    group1.add_argument("-ver", choices=['101','105','110'],
            help="Newnslog version",required=True,metavar='VER')
    group1.add_argument("-infile", help="Logfile to parse",
            required=True,metavar='PATH')
    args = parser.parse_args()
    logfile = args.infile
    ver = args.ver
    curses.wrapper(main)

def main(win):
    """Main control flow"""
    global stdscr
    stdscr = win
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)
    curses.curs_set(0)
    y,x=0,1
    dataspool = Data_build()
    ns_source = Nstools(logfile,ver)
    #running = False
    #curses.nocbreak()
    #stdscr.keypad(0)
    #curses.echo()
    #curses.endwin()
    #import pdb; pdb.set_trace()

    log_generator = ns_source.nratechecker()
    
    for index,data in enumerate(log_generator):
        dataspool.add_data(data)
    
    #start of window creation
    maxcoords = stdscr.getmaxyx()
    max_Y,max_X = maxcoords[y],maxcoords[x]
    stdscr.refresh()
    cwin = BaseWin(max_Y,max_X)
    dataspool.prep_data(cwin.bborder,max_X)
    cwin.Intro_Option_draw()#intro screen
    while not cwin.introdone:
        keypress = stdscr.getch()
        if keypress == ord('Q'):
            return
            sys.exit()
        elif keypress == ord(' '):
             cwin.Intro_option_select()
   
    cwin.Main_Cselect(dataspool.topclist(),dataspool.shallow_ret())
    running = True
    while running:
        keypress = stdscr.getch()
        if keypress == ord('Q'):
            running = False
            return
        elif keypress == ord('L') and cwin.context == 3:
            cwin.toggle_legend()
        elif keypress == curses.KEY_DOWN:
            if cwin.context == 1:
                cwin.m_selectdown()
            elif cwin.context == 2:
                cwin.s_selectdown()
            elif cwin.context == 3:
                pass
        elif keypress == curses.KEY_UP:
            if cwin.context == 1:
                cwin.m_selectup()
            elif cwin.context == 2:
                cwin.s_selectup()
            elif cwin.context ==3 :
                pass
        elif ((keypress == curses.KEY_ENTER) or (keypress == 10) or (keypress == 13) or (keypress == curses.KEY_RIGHT)):
            if cwin.context == 1:
                cwin.context = 2
                cwin.p_jump()
            if cwin.context == 3:
                #clear of current window, redraw +1 screenlen with new offset
                curcounter = cwin.countplotdict.keys()[cwin.panmvloc]
                cwin.clear_graph(cwin.panmvloc)
                #some logic to decide on index to read next sequence of values
                #necessary to logically lay out and draw sane graphs
                #also allowing for movement through the graph
                
                for i, dev in enumerate(cwin.countplotdict[curcounter]):
                    if dataspool.drawtrack[curcounter][dev]['overallen'] < max_X:
                        #offset is a count of the current offset from the start of the valuelist
                        dataspool.drawtrack[curcounter][dev]['offset'] = 0
                    elif dataspool.drawtrack[curcounter][dev]['offset'] + max_X < dataspool.drawtrack[curcounter][dev]['overallen']:
                        #if we can fit another x-axis len of values to screen
                        dataspool.drawtrack[curcounter][dev]['offset'] += max_X #move one screen len in offset
                    curoffset = dataspool.drawtrack[curcounter][dev]['offset']
                    
                    refillsource = dataspool.read_full_rate_data(curcounter,dev,curoffset)
                    
                    timecount = cwin.lborder
                    for timenotch,val in refillsource:
                        cwin.spray_dots(val,timenotch-curoffset,cwin.panmvloc,i)
                        if timecount == cwin.lborder: #first occurrence, write first timestamp
                            cwin.annotate_x_day(cwin.panmvloc,dataspool.find_time(timenotch,type='general'),timecount)
                            cwin.annotate_x_time(cwin.panmvloc,dataspool.find_time(timenotch),timecount)
                        elif timecount % 30 == 0:
                     
                            cwin.annotate_x_time(cwin.panmvloc,dataspool.find_time(timenotch),timecount)
                        timecount += 1

                cwin.one_refresh(cwin.panmvloc)

        elif (keypress == ord('\t') or keypress == 9 or keypress == curses.KEY_PPAGE) and cwin.context == 3:
            #if tab or page up, show next panel
            cwin.graphshow(1)
        
        elif (keypress == curses.KEY_BACKSPACE) or (keypress == curses.KEY_LEFT):
            #context 1 = counter selection
            #context 2 = device selection
            #context 3 = graph move / show
            if cwin.context == 2:
                cwin.context = 1
                cwin.m_jump()
            if cwin.context == 3:
                curcounter = cwin.countplotdict.keys()[cwin.panmvloc]
                cwin.clear_graph(cwin.panmvloc)
                
                for i, dev in enumerate(cwin.countplotdict[curcounter]):
                    if dataspool.drawtrack[curcounter][dev]['offset'] - max_X >= 0:
                        dataspool.drawtrack[curcounter][dev]['offset'] -= max_X
                    else:
                        dataspool.drawtrack[curcounter][dev]['offset'] = 0
                    timecount = cwin.lborder #indexing positions on x axis from lborder, that's all
                    curoffset = dataspool.drawtrack[curcounter][dev]['offset']
                    refillsource = dataspool.read_full_rate_data(curcounter,dev,curoffset)
                    for timenotch,val in refillsource:
                        cwin.spray_dots(val,timenotch-curoffset,cwin.panmvloc,i)
                        if timecount == cwin.lborder: #first occurrence, write first timestamp
                            cwin.annotate_x_day(cwin.panmvloc,dataspool.find_time(timenotch,type='general'),timecount)
                            cwin.annotate_x_time(cwin.panmvloc,dataspool.find_time(timenotch),timecount)
                        elif timecount % 30 == 0:
                     
                            cwin.annotate_x_time(cwin.panmvloc,dataspool.find_time(timenotch),timecount)
                        timecount += 1
                       
                cwin.one_refresh(cwin.panmvloc)
        
        elif (keypress == curses.KEY_BTAB or keypress == curses.KEY_NPAGE) and cwin.context == 3:
            cwin.graphshow(-1)

        elif (keypress == ord(' ')) and cwin.context == 2:
            cwin.dev_toggle()

        elif keypress == ord('H') or keypress == ord('h'): 
            cwin.showing_help = True
            cwin.Help_Draw()
            while cwin.showing_help:
                helppress = stdscr.getch()
                if helppress == ord('H'):
                    cwin.Help_Dismiss()
        
        #Fire up the graph windows ->
        elif ((keypress == ord('G')) or (keypress == ord('g'))) and cwin.context == 2:
            cwin.context = 3
            curoffset = 0
	    cwin.generate_graphPanels()
            for index,counter in enumerate(cwin.countplotdict):
                
                for dev in cwin.countplotdict[counter]:
                    dataspool.fillmaxminvals(counter,dev)
                
                for ylocindex, dev in enumerate(cwin.countplotdict[counter]):
                    cwin.addname(dev, ylocindex, index)
                    valuesource = dataspool.read_full_rate_data(counter,dev)
                    timecount = cwin.lborder
                    
                    for timenotch,val in valuesource:
                        cwin.spray_dots(val,timenotch,index,ylocindex)
                        
                        #Annotate x graph values for the first time while we're iterating through dev values ->
                        
                        if timecount == cwin.lborder: #first occurrence, write first timestamp
                            cwin.annotate_x_day(index,dataspool.find_time(timenotch,type='general'),timecount)
                            cwin.annotate_x_time(index,dataspool.find_time(timenotch),timecount)
                        elif timecount % 30 == 0:
                     
                            cwin.annotate_x_time(index,dataspool.find_time(timenotch),timecount)
                        timecount += 1

            cwin.one_refresh(cwin.panmvloc)
            
            #now annotate y graph values on the left ->

            #TODO - truncate long values (anything over 4 characters) 
            #       to save screen space
            for index, counter in enumerate(cwin.countplotdict):
                
                for i in xrange(4,-1,-1):
                    if counter == ('cc_cpu_use' or 'cpu_use' or 'master_cpu_use' or 'mgmt_cpu_use'): #hardwiring CPU values
                        if i == 0:
                            val = 0
                            yoffset = cwin.bborder-1#always on bottom
                        elif i == 4:
                            val = 100
                            yoffset = 0#always at the top
                        else:
                            val = int(100 * (.25 * i))
                            yoffset = cwin.bborder - (int(cwin.bborder/4) * i)#remaining 1/4 screen indices
                    else:
                        if i == 0:
                            val = dataspool.maxmindict[counter]['minrate']
                            yoffset = cwin.bborder -1 #on the bottom
                        elif i == 4:
                            val = dataspool.maxmindict[counter]['maxrate']
                            yoffset = 0
                        else:
                            val = int(dataspool.maxmindict[counter]['spanrate'] * (.25 * i)) + dataspool.maxmindict[counter]['minrate']
                            yoffset = cwin.bborder - (int(cwin.bborder/4) * i)

                    cwin.annotate_y(index,yoffset,val)

                    cwin.one_refresh(index)

        elif (keypress == ord('R')) and cwin.context == 3:
            #(R)edraw the counter selection, delete dataspool attributes
            cwin.hide_graphPanels()
            dataspool.resetcounters()
            cwin.context = 2
            cwin.refresh()

    #end of program clean up
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()

if __name__=='__main__':
    check_args()



#running = False
#curses.nocbreak()
#stdscr.keypad(0)
#curses.echo()
#curses.endwin()
#import pdb; pdb.set_trace()

