#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paramiko
import getpass
import time
import sys
import argparse
from swtools import grepList, hpConnect, huaweiConnect, getVendor

#DEBUG = True

__author__ = 'Xisco Chacon'

parser = argparse.ArgumentParser(description='Script para actualizar el firmware de un switch HP')
parser.add_argument('-i','--switch_ip',help='IP del switch definido en Pandora', required=True)
parser.add_argument('-d','--switch_debug',type=bool, default=False, help='Modo Debug')
parser.set_defaults(reboot=False)
args = parser.parse_args()

#ip = raw_input("Enter Host: ")
ip=args.switch_ip
debug=args.switch_debug
DEBUG=debug

def grepList(string, filter):
    fOut=[]
    for line in string.splitlines():
        if filter.upper() in line.upper(): 
            fOut.append(line)
    return fOut

def sendCommand(rem_con, command, t=1):
    remote_conn.send(command+'\n') 
    time.sleep(t)
    out = remote_conn.recv(5000).decode("utf-8")
    if DEBUG: print out
    return out


if DEBUG: print getVendor(ip)


