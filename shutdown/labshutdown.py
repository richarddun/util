#!/usr/bin/env python2
"""Script to automate shutdown of a lab environment
   containing CloudBridge/NetScaler/SDX devices.
   It is an exercise in Paramiko and Nitro and RESTful
   API exposed on these appliances.
   
   Expects a csv list available in the same directory 
   as the script called devices.csv, which contains:
   ip_address,name-label(any name),params

   where params are : 

   device-type = netscaler or cloudbridge or sdx
   username (for login)
   password (for login)

   Format (in the case of an sdx):

   ip_address,name-label,sdx:nsroot:nsroot

   script requires (in addition to stdlib) :
   Paramiko
   NetScaler Nitro SDK for Python
   """

import json
import urllib2
import paramiko
import csv
import ssl
import os
from nssrc.com.citrix.netscaler.nitro.resource.config import *
from nssrc.com.citrix.netscaler.nitro.service.nitro_service import nitro_service as nssvc

def dev_details():
    """Runs csv reader, creates generator to return
    a list of each row in the csv file containing all 
    items which are not null"""
    templist = []
    with open('devices.csv','rb') as csvfile:
        devitems = csv.reader(csvfile)
        for row in devitems:
            for item in row:
                if len(item) > 1:
                    templist.append(item)
            yield templist
            templist = []

class SvmOperation:
    """Class to operate on SVM(NS)"""
    def __init__(self,ipaddr):
        """Retrieves auth sessionid as part of instantiation
           Accepts a list containg IP, ID, Params"""
        _self.context =  ssl._create_unverified_context()
        _self.ip_addr = ipaddr
        _self.login_payload = json.dumps({"login": {"username": "nsroot", "password": "nsroot"}})
        _self.clen = len(_self.login_payload)
        _self.loginurl = 'https://'_self.ip_addr+'/nitro/v2/config/login'
        _self.loginreq = urllib2.Request(_self.loginurl,_self.login_payload)
        _self.loginreq.add_header('Content-Type','Content-Type:application/vnd.com.citrix.sdx.login+json')
        _self.loginreq.add_header('Content-Length',_self.clen)
        _self.response = json.load(urllib2.urlopen(_self.loginreq,context=_self.context))
        self.sessionid = _self.response['login'][0]['sessionid']

    def svm_enum_ns_resource(self):
        """Enumerates all running NS instances, returning 
           their IP addresses in a list"""
        self.retlist = []
        getaddr = 'https://'+_self.ip_addr+'/nitro/v2/config/ns'
        enum_req = urllib2.Request(getaddr)
        enum_req.add_header('Cookie','NITRO_AUTH_TOKEN='+self.sessionid)
        enum_req.add_header('Content-Type','application/vnd.com.citrix.sdx.ns+json')
        enumstream = json.load(urllib2.urlopen(enum_req,context=_self.context))
        for ns in enumstream['ns']:
            if ns['vm_state'] == 'Running':
                self.retlist.append(ns['ns_ip_address'])
        return self.retlist

def nitro_ns_savec(devdetails=None, mgmtip=None):
    """uses nitro to login to a NS, saving the current configuration. 
    Takes a list as argument (containing IP, name, params)"""
    ip_addr,id_name,params = 0,1,2 #english indexing
    if mgmtip = None:
        ns_session = nssvc(devdetails[ip_addr],'https')
        username = devdetails[params].split(':')[1]
        password = devdetails[params].split(':')[2]
    else:
        ns_session = nssvc(mgmtip,'https')
        username,password = 'nsroot','nsroot'
    ns_session.certvalidation = False
    ns_session.hostnameverification = False
    ns_session.login(username,password,3600)
    confobj = nsconfig
    confobj.save(ns_session)

def discover_svm_ip(devdetails):
    """Uses paramiko to ssh to XS, then relay to 169.x address
       of svm, and issues show networkconfig, plucking the 
       SVM IP and returning it as a string"""
    ip_addr,id_name,params = 0,1,2 #english indexing
    user = devdetails[params].split(':')[1]
    passwd = devdetails[params].split(':')[2]
    ssh_conn = paramiko.SSHClient()
    ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_conn.connect(ip_addr,username=user,password=passwd)
    chan = ssh_conn.invoke_shell()
    chan.send('ssh nsroot@169.254.0.10\n')
    _ = chan.recv(9999)
    time.sleep(1)
    chan.send('nsroot\n')
    _ = chan.recv(9999)
    time.sleep(2)
    chan.send('show networkconfig\n')
    time.sleep(4)    
    data = chan.recv(9999)
    details = data.splitlines()
    svmdet = details[7]
    svmip = svmdet.split(': ')[1]
    ssh_conn.close()
    return svmip

def xs_shutdown(ipaddr):
    """Convenience function to shutdown XS with paramiko"""
    ssh_conn = paramiko.SSHClient()
    ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_conn.connect(ipaddr,username='nsroot',password='nsroot')
    chan = ssh_conn.invoke_shell()
    chan.send('shutdown -h now\n')

def ns_kern_shutdown(ipaddr):
    """Paramiko calls to shutdown NS"""
    ssh_conn = paramiko.SSHClient()
    ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_conn.connect(ipaddr,username='nsroot',password='nsroot')
    chan = ssh_conn.invoke_shell()
    chan.send('shutdown\n')
    time.sleep(1)
    chan.send('Y\n')

def cb_xs_shutdown(devdetails):
    """uses paramiko to SSH to a box and shut it down
     takes a list as argument (containing IP, name, params)"""
    ip_addr,id_name,params = 0,1,2 #english indexing
    user = devdetails[params].split(':')[1]
    passwd = devdetails[params].split(':')[2]
    ssh_conn = paramiko.SSHClient()
    ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    chan = ssh_conn.invoke_shell()
    chan.send('shutdown -h now\n')

def cb_hw_shutdown(devdetails):
    """Paramiko calls to shutdown h/w CB.  Takes a list as 
       argument (containing IP,name,params(user:pass))"""
    ip_addr,id_name,params = 0,1,2 #english indexing
    user = devdetails[params].split(':')[1]
    passwd = devdetails[params].split(':')[2]
    ssh_conn = paramiko.SSHClient()
    ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    chan = ssh_conn.invoke_shell()
    chan.send('shutdown -h now\n')

def is_cb_svm(ipaddr):
    """Does a RESTful call to CB specific URL path.  If 404 
       error is returned, this is not a CB SVM"""
    context =  ssl._create_unverified_context()
    req = urllib2.Request('https://'+ipaddr+'/cb/nitro/v1/config/system_info')
    req.add_header('Authorization','Basic bnNyb290Om5zcm9vdA==')
    req.add_header('Accept','*/*')
    try:
        res = urllib2.urlopen(req,context=context)
        if res:
            return True
    except urllib2.HTTPError:
        return False

def lab_shutdown():
    """main"""
    success_list = []
    failure_list = []
    login_details = 3 #english indexing is friendlier
    devs_to_shutdown = dev_details()
    for dev in devs_to_shutdown:
        if dev[login_details].split(':')[0] == 'sdx':
            svm_ip = discover_svm_ip(dev)
            if is_cb_svm(svm_ip):
                cb_xs_shutdown(dev[0])
            else:
                thisdev = SvmOperation(svm_ip)
                nsiplist = thisdev.enum_ns_resources()
                for nsip in nsiplist:
                    nitro_ns_savec(mgmtip=nsip)
                xs_shutdown(dev[0])
        elif dev[login_details].split(':')[0] == 'netscaler':
            nitro_ns_savec(dev)
            ns_kern_shutdown(dev[0])
        elif dev[login_details].split(':')[0] == 'cloudbridge':
            cb_hw_shutdown(dev)#requires root account access to 
                               #old 'branch repeater' models

if __name__== '__main__':
    lab_shutdown()


