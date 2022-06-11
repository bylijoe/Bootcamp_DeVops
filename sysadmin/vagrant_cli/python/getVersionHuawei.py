#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paramiko
import getpass
import time
import sys
import socket
from swtools import grepList

DEBUG = False


def printVer(sw):
    username = 'adminjgp'
    password = 'ViVaHoTeLS'
    
    try:
        remote_conn_pre = paramiko.SSHClient()
        remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        remote_conn_pre.connect(sw, username=username, password=password, allow_agent=False, look_for_keys=False, timeout=5)
    except socket.timeout:
        print "%s: Error de conexion" % sw
        sys.exit(1)
    except:
        print "%s: Error no esperado" % sw
        sys.exit(1)
    
    if DEBUG: print ("SSH connection established to %s" % sw)
    remote_conn = remote_conn_pre.invoke_shell()   
    time.sleep(1)
    output = remote_conn.recv(1000).decode("utf-8")
    prompt = output.strip()
    prompt= prompt.splitlines()
    prompt=prompt[-1]
    if DEBUG: print prompt
    if DEBUG: print output
        
        
    #remote_conn.send('terminal length 0\n')
    #time.sleep(1)
    #output = remote_conn.recv(1000).decode("utf-8")
    remote_conn.send('dis ver\n')
    time.sleep(1)
    output = remote_conn.recv(5000).decode("utf-8")
    if DEBUG: print output
    sw_ver = grepList(output, 'vrp')[0].split()[-1].replace(')','')
    swModel=grepList(output, 'uptime')[0].split()[1] 
    hostname = prompt.replace('<','').replace('>','')
    print '%s;%s;%s' %  (hostname,swModel,sw_ver)
    remote_conn.close()
    
listaSW=[]

if len(sys.argv) >= 2:
    listaSW=sys.argv[1:len(sys.argv)]
    for sw in listaSW:
        printVer(sw)
else:
    print "Ningun switch a consultar"

exit()    