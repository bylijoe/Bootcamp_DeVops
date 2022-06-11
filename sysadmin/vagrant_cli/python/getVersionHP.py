#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paramiko
import getpass
import time
import sys
import socket
from swtools import grepList,hpConnect,getHPver

DEBUG = False

  
def printVer(sw):
    #username = 'admin'
    ##password = getpass.getpass()
    #hoteles = { '17.1' : 'club',
    #            '17.2' : 'resort',
    #            '17.3' : 'suite',
    #            '16.3' : 'tropic',
    #            '16.4' : 'golf',
    #            '16.5' : 'sunrise',
    #            '16.6' : 'palmanova',
    #            '16.8' : 'bahia',
    #            '16.11' : 'picafort',
    #            '16.12' : 'menorca',
    #            '16.14' : 'blue',
    #            '16.19' : 'mallorca',
    #            '16.22' : 'edenlago',
    #            '16.23' : 'binibeca',
    #            '16.25' : 'rey',
    #            '16.26' : 'zafiro',
    #}
    #password = 'W'+ hoteles['.'.join(sw.split('.')[1:3])] + '01'
    #
    #try:
    #    remote_conn_pre = paramiko.SSHClient()
    #    remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())     
    #    remote_conn_pre.connect(sw, username=username, password=password, allow_agent=False, look_for_keys=False, timeout=5)
    #except paramiko.AuthenticationException:
    #    if DEBUG: print "Error autenticacion"
    #    try:
    #        remote_conn_pre.connect(sw, username=username, password='PASSWORD', allow_agent=False, look_for_keys=False, timeout=5)
    #    except:
    #        print "%s: Error de autenticacion" % sw
    #        sys.exit(1)
    #except socket.timeout:
    #    print "%s: Error de conexion" % sw
    #    sys.exit(1)
    #except:
    #    print "%s: Error no esperado" % sw
    #    sys.exit(1)
    remote_conn_pre = hpConnect(sw)       
    if DEBUG: print ("SSH connection established to %s" % sw)
    remote_conn = remote_conn_pre.invoke_shell()   
    time.sleep(1)
    output = remote_conn.recv(1000).decode("utf-8")
    
    prompt = output.strip()
    prompt= prompt.splitlines()
    prompt=prompt[-1]
    if DEBUG: print prompt
    if DEBUG: print output
    hostname = prompt.replace('<','').replace('>','')
    #obtener version
    #remote_conn.send('summary\n')
    #remote_conn.send(' ')
    #time.sleep(1)
    #output = remote_conn.recv(5000).decode("utf-8")
    #if DEBUG: print output
    #if 'uptime' in output:
    #    sw_ver=grepList(output, 'Release')[0].split()[-1].replace(')','')
    #    swModel=grepList(output, 'uptime')[0].split('uptime')[0] 
    #    hostname = prompt.replace('<','').replace('>','')
    #    print '%s;%s;%s' %  (hostname,swModel,sw_ver)
    #else:
    #    print '%s Switch no HP' % sw
    
    (swModel,sw_ver) = getHPver(remote_conn)
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