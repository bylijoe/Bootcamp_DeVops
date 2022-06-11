#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import paramiko
import os
import sys
import time

def readInt(m, max):
    print '[%d] %s' % (0, 'Exit')
    retries = 3
    for ret in range(0,retries):
        try:
            num = int(raw_input(m))
            print num
            if num in range(1,max+1):
                return num
            elif num == 0:
                print 'es cero'
                break
            else:
                print 'Numero introducido no válido'
        except:
            print 'Numero introducido no valido'
        

print readInt('Introduzca un numero del 1 al 5: ', 5)
