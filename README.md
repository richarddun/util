
#constellation

Given a collection of formatted strings containing entity_name, rate_count and time, this program will attempt to parse and draw a simple graph using the Curses wrapper in Python 2.7
(Work in progress)

#norblog

Log reading script for .Orblog files produced when creating a Diagnostic file from a Citrix CloudBridge appliance.  These files are usually not stored in ascii and need to be filtered
for human reading.  This script operates on an extracted directory containing .Orblog files and outputs a human readable text file.  

#shutdown

Exercise in using Nitro API, RESTful interface to interact with a Citrx NetScaler or Citrix CloudBridge appliance.  This program, given a csv list of ip addresses (and additional
identification parameters, see the src) will attempt to log in, enumerate active resources, save configuration on any active instances, and shutdown each appliance / entity at the
provided IP address.  Also uses Paramiko to handle unsupported operations via REST/Nitro SDX for Python
