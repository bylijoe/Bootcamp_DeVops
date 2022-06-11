#!/usr/bin/env python

import paramiko
import os
import sys
import time
from aerohive import flash


listaAPs=[]
if len(sys.argv) >= 2:
    listaAPs=sys.argv[1:len(sys.argv)]
    for ap in listaAPs:
        #print ap
        flash(ap)
        if len(listaAPs)>1: raw_input('Intro para continuar.')
else:
    print "Ningun AP a configurar"

exit()
