#!/usr/bin/env python

import paramiko
import os
import sys
import time
from aerohive import hideSSID

'''def hideSSID(ap):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print "conectando a %s" % ap
    try:
        ssh.connect(ap, username='admin', password='PASSWORD',timeout=2)
        shell = ssh.invoke_shell()
        time.sleep(2)
        print "SSID visible"
        shell.send('no ssid Vivacorporativo hide-ssid\n')
        print "sleep"
        time.sleep(2)
        print "Ocultando SSID"
        shell.send('ssid Vivacorporativo hide-ssid\n')
        time.sleep(2)
        shell.send('save config running current\n')
        ssh.close()
    except:
        print "No se puede establecer la conexion con %s" % ap
		'''

listaAPs=[]
c=0
if len(sys.argv) >= 2:
    if any('all' in s for s in sys.argv):
	print 'Todos los AP170 van a corregir el SSID Vivacorporativo'
        ap170=open('ap170.csv')
        while True:
            ap = ap170.readline()
            if not ap: break
            if ap.startswith('AH'):
                listaAPs.append(ap.split(';')[1].replace('\n',''))
#        print listaAPs    
        ap170.close()
    else:
        listaAPs=sys.argv[1:len(sys.argv)]
    for ap in listaAPs:
        c+=1
        print "%d - %s" % (c,ap)
        #print ap
        hideSSID(ap)
else:
    print "Ningun AP a configurar"

exit()
