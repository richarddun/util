#!/usr/bin/env python2
"""Main program control and logic"""

import argparse
import os
import sys
import subprocess
import re
from datahandler import *
from display import *


#handle user input
parser = argparse.ArgumentParser(description ='Rate count visualiser')
group1 = parser.add_argument_group('required arguments')
group1.add_argument("-ns", metavar='Use if logfile is newnslog')
group1.add_argument("-ver", choices=['101','105','110'],
        help="Newnslog version")
group1.add_argument("-infile", help="Logfile to parse",
        required=True,metavar='PATH')
args = parser.parse_args()

logfile = args.infile

dataspool = Data_build()
dataspool.open_hash(logfile)
ns_source = Nstools()
log_generator = ns_source.nratechecker()
for data in log_generator:
    dataspool.add_data(data)

dataspool.sync_hash()
dataspool.close_hash()














#if __name__ == '__main__':
#    ratechecker()

