#!/usr/bin/env python2
"""Main program control and logic"""

import argparse
import os
import sys
import subprocess
import re
import curses
from datahandler import *
from display import *

def check_args():
    global ver,logfile
    parser = argparse.ArgumentParser(description ='Rate count visualiser')
    group1 = parser.add_argument_group('required arguments')
#    group1.add_argument("-ns", metavar='Use if logfile is newnslog')
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
    dataspool.open_hash(logfile)
    ns_source = Nstools(logfile,ver)
    log_generator = ns_source.nratechecker()
    synccount = 1
    for data in log_generator:
        dataspool.add_data(data)
        if synccount % 50 == 0:
            dataspool.sync_hash()
        synccount += 1
    dataspool.sync_hash()
    dataspool.close_hash()

    #start of window creation
    maxcoords = stdscr.getmaxyx()
    max_Y,max_X = maxcoords[y],maxcoords[x]
    db_str = logfile + '.db'
    dataspool.open_hash(db_str)
    stdscr.refresh()#inexplicably, this is required
    cwin = BaseWin(max_Y,max_X)
    cwin.Main_Cselect(dataspool.topclist(),dataspool.shallow_ret())
    running = True
    while running:
        keypress = stdscr.getch()
        if keypress == ord('Q'):
            running = False
            return
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
        elif ((keypress == curses.KEY_ENTER) or (keypress == 10) or (keypress == 13) or (keypress == curses.KEY_RIGHT)) and cwin.context == 1:
            cwin.context = 2
            cwin.p_jump()
        elif (keypress == curses.KEY_BACKSPACE) or (keypress == curses.KEY_LEFT):
            cwin.context = 1
            cwin.m_jump()
        elif (keypress == ord(' ')) and cwin.context == 2:
            cwin.dev_toggle()








    #end of program clean up
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()

#dataspool.close_hash()

if __name__=='__main__':
    check_args()

