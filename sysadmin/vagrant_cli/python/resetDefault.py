#!/usr/bin/env python
import paramiko
import os
import sys
import time
from aerohive import resetDefault



listaAPs=[]

if len(sys.argv) >= 2:
    listaAPs=sys.argv[1:len(sys.argv)]
    for ap in listaAPs:
        if 'lst' in ap:
            print 'Se van a encender los LEDs de los APs listados en %s' % ap
            apList=open(ap)
            while True:
                l = apList.readline()
                if not l: break
                resetDefault(l)
        #print ap
        else:
            resetDefault(ap)
#        if len(listaAPs)>1: raw_input('Intro para continuar.')
else:
    print "Ningun AP a configurar"

exit()
