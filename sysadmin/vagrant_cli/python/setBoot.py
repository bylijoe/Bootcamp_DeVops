#!/usr/bin/env python

import paramiko
import os
import sys
import time
from aerohive import configBoot




'''listaAPs=[]
if len(sys.argv) >= 2:
    if any('all' in s for s in sys.argv):
	print 'Todos los AP del fichero inventario van a configurar el boot por tftp'
        accessPoints=open('inventario')
        while True:
            ap = accessPoints.readline()
            if not ap: break
            if ap.startswith('10.'):
                listaAPs.append(ap.replace('\n',''))
#        print listaAPs    
        accessPoints.close()
    else:
	    listaAPs=sys.argv[1:len(sys.argv)]
    for ap in listaAPs:
        #print ap
        hideSSID(ap)
else:
    print "Ningun AP a configurar"
    '''



listaAPs=[]
c=0
if len(sys.argv) >= 2:
    if any('all' in s for s in sys.argv):
        print 'Todos los AP del fichero inventario.lst van a configurar el boot por tftp'
        raw_input('Intro para continuar.')
        accessPoints=open('inventario.lst')
        while True:
            ap = accessPoints.readline()
            if not ap: break
            if ap.startswith('172.'):
                listaAPs.append(ap.replace('\n',''))
#        print listaAPs    
        accessPoints.close()
    else:
        listaAPs=sys.argv[1:len(sys.argv)]
    for ap in listaAPs:
        c+=1
        print "%d - %s" % (c,ap)
        configBoot(ap)
        #if len(listaAPs)>1: raw_input('Intro para continuar.')
else:
    print "Ningun AP a configurar"

exit()
