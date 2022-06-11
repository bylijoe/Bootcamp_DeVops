#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paramiko
import getpass
import time
import sys
from swtools import grepList, expect, readInt, readAns, grep,hpConnect

#DEBUG = True
DEBUG = False

ip = raw_input("Enter Host: ")

FTP_SERVER='192.168.252.100'
TFTP_SERVER='192.168.252.100'

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

print "Modelo: %s;" % swModel
print "Firmware: %s;" % firmware


if ('1910' or 'Baseline') in swModel:
    if DEBUG: print "modelo 1910"
    fwFile="V1910-CMW520-R1518P01.bin"
    sysPasswd='512900'
elif '1920' in swModel:
    fwFile="JG926A-CMW520-R1113.bin"
    if DEBUG: print "modelo 1920"
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

#salvar configuracion y reiniciar
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
