#!/usr/bin/env python

import paramiko
import os
import sys
import time

def showNeigbours(ap):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print "conectando a %s" % ap
    ssh.connect(ap, username='admin', password='PASSWORD')
    shell = ssh.invoke_shell()
    shell.send('show running-config | include neigh\n')
    output = shell.recv(5000)
    print len(output)
    print output
    ssh.close()

if len(sys.argv) >= 2:
    for ap in sys.argv[1:len(sys.argv)]:
        showNeigbours(ap)
else:
    print "Ningun AP a configurar"

exit()
