#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import paramiko
import getpass
import time
import sys
from swtools import grepList, expect, readInt, readAns, grep,hpConnect


__author__ = 'Julian Garcia-Sotoca Pascual'

DEBUG = False

parser = argparse.ArgumentParser(description='Script para corregir parametros de snmp en switches')
parser.add_argument('-i','--ip',help='IP del switch', required=True)
parser.add_argument('-l','--location',help='ubicacion', required=True)
parser.add_argument('-c','--contact',help='Contacto', required=False)
args = parser.parse_args()


#ip = raw_input("Enter Host: ")
ip = args.ip
#contact = raw_input("Contacto [Julian Garcia-Sotoca <sistemas@zafirohotels.com>]: ")
if not args.contact: 
    contact = "Julian Garcia-Sotoca <sistemas@zafirohotels.com>"
else:
    contact =  args.contact
#location = raw_input("Ubicacion: ")
location = args.location


remote_conn_pre = hpConnect(ip) 
remote_conn = remote_conn_pre.invoke_shell()   
time.sleep(1)
output = remote_conn.recv(1000).decode("utf-8")

prompt = output.strip()
prompt= prompt.splitlines()
prompt=prompt[-1]
if DEBUG: print prompt
if DEBUG: print output

#obtener version
remote_conn.send('summary\n')
remote_conn.send(' ')
time.sleep(1)
output = remote_conn.recv(5000).decode("utf-8")
if DEBUG: print output

firmware=grepList(output, 'Release')[0].split()[-1].replace(')','')
swModel=grepList(output, 'uptime')[0].split('uptime')[0] 

print "Modelo: %s" % swModel
print "Firmware: %s" % firmware

if '1910' in swModel:
    if DEBUG: print '1910'
    fwFile="V1910-CMW520-R1518P01.bin"
    sysPasswd='512900'
elif 'Baseline' in swModel:    
    if DEBUG: print 'Baseline'
    fwFile="V1910-CMW520-R1518P01.bin"
    sysPasswd='512900'
elif '1920' in swModel:
    if DEBUG: print '1920'
    fwFile="JG926A-CMW520-R1113.bin"
    sysPasswd='Jinhua1920unauthorized'
else:
    print 'Modelo no especificado. Salimos'
    exit(1)

if DEBUG: print fwFile
if DEBUG: print sysPasswd

#pasar a modo avanzado:
remote_conn.send('_cmdline-mode on\n')
time.sleep(1)
output = remote_conn.recv(5000).decode("utf-8")
if DEBUG: print output
remote_conn.send('Y\n')
time.sleep(1)
remote_conn.send('%s\n' % sysPasswd)
output = remote_conn.recv(5000).decode("utf-8")
if DEBUG: 
    print output
    remote_conn.send('dis ver\n')
    time.sleep(1)
    output = remote_conn.recv(5000).decode("utf-8")
    print output

#corregir snmp
remote_conn.send('sys\n') 
time.sleep(1)
output = remote_conn.recv(5000).decode("utf-8")
remote_conn.send('snmp-agent community read V1vaH0tels\n') 
time.sleep(1)
output = remote_conn.recv(5000).decode("utf-8")
remote_conn.send('snmp-agent sys-info contact %s\n' % contact)
time.sleep(1)
output = remote_conn.recv(5000).decode("utf-8")
remote_conn.send('snmp-agent sys-info location %s\n' % location)
time.sleep(1)
output = remote_conn.recv(5000).decode("utf-8")
remote_conn.send('snmp-agent sys-info version v1 v3\n')
time.sleep(1)
output = remote_conn.recv(5000).decode("utf-8")

    
if DEBUG: print output    
#salvar configuracion
remote_conn.send('save\n')
time.sleep(5)
output = remote_conn.recv(1000).decode("utf-8")
print output
if '[Y/N]' in output: remote_conn.send('Y\n')
time.sleep(1)
output = remote_conn.recv(1000).decode("utf-8")
print output
remote_conn.send('\n')
time.sleep(1)
output = remote_conn.recv(1000).decode("utf-8")
print output
remote_conn.send('Y\n')
time.sleep(1)
output = remote_conn.recv(1000).decode("utf-8")
print output
    
    
remote_conn.close()



    