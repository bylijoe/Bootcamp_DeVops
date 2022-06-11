#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paramiko
import getpass
import time
import sys
import argparse
from swtools import grepList, expect, readInt, readAns, grep, hpConnect

DEBUG = False

__author__ = 'Julian Garcia-Sotoca Pascual'
parser = argparse.ArgumentParser(description='Script para actualizar el firmware de un switch HP')
parser.add_argument('-i','--switch_ip',help='IP del switch definido en Pandora', required=True)
parser.add_argument('-r', '--reboot', dest='reboot', action='store_true')
parser.add_argument('-n', '--no-reboot', dest='reboot', action='store_false')
parser.set_defaults(reboot=False)
args = parser.parse_args()


#ip = raw_input("Enter Host: ")
ip=args.switch_ip


FTP_SERVER='192.168.254.127'
TFTP_SERVER='192.168.254.127'

remote_conn_pre = hpConnect(ip) 
remote_conn = remote_conn_pre.invoke_shell()   
time.sleep(1)
OUTPUT = remote_conn.recv(1000).decode("utf-8")

PROMPT = OUTPUT.strip()
PROMPT= PROMPT.splitlines()
PROMPT=PROMPT[-1]
if DEBUG: print 'PROMPT: '+PROMPT
if DEBUG: print OUTPUT

#obtener version
remote_conn.send('summary\n')
remote_conn.send(' ')
time.sleep(1)
OUTPUT = remote_conn.recv(5000).decode("utf-8")
if DEBUG: print OUTPUT

firmware = grepList(OUTPUT, 'Release')[0].split()[-1].replace(')','')
swModel = grepList(OUTPUT, 'uptime')[0].split('uptime')[0] 

print "Modelo: %s" % swModel
print "Firmware: %s" % firmware

#pasar a modo avanzado:
if ('1910' or 'Baseline') in swModel:
    FWFILE = "1910-CMW520-R1519P03.bin"
    SYSPASSWD = '512900'
    remote_conn.send('_cmdline-mode on\n')
elif '1920' in swModel:
    FWFILE = "JG926A-CMW520-R1119.bin"
    SYSPASSWD = 'Jinhua1920unauthorized'
    if '1113' in firmware:
        remote_conn.send('\_cmdline-mode on\n')
    else:
        remote_conn.send('_cmdline-mode on\n')
else:
    print 'Modelo no especificado. Salimos'
    exit(1)

if DEBUG: print FWFILE
if DEBUG: print SYSPASSWD



time.sleep(1)
OUTPUT = remote_conn.recv(5000).decode("utf-8")
if DEBUG: print OUTPUT
remote_conn.send('Y\n')
time.sleep(1)
remote_conn.send('%s\n' % SYSPASSWD)
OUTPUT = remote_conn.recv(5000).decode("utf-8")
if DEBUG:
    print OUTPUT
    remote_conn.send('dis ver\n')
    time.sleep(1)
    OUTPUT = remote_conn.recv(5000).decode("utf-8")
    print OUTPUT

#borrar imagenes antiguas
remote_conn.send('dir\n')
time.sleep(1)
OUTPUT = remote_conn.recv(5000).decode("utf-8")
for line in OUTPUT.splitlines():
    if line.endswith('.bin'):
        oldfw = line.split()[-1]
        delfile = readAns('Borrar firmware %s [Y/N]' % oldfw)
        if delfile == 'Y':
            remote_conn.send('del %s\n' % oldfw)
            time.sleep(1)
            OUTPUT = remote_conn.recv(5000).decode("utf-8")
            remote_conn.send('Y\n')
            time.sleep(1)
            OUTPUT = remote_conn.recv(5000).decode("utf-8")
            if DEBUG: print OUTPUT
    elif 'free' in line:
        print 'Espacio libre en flash: %s' % line.split('(')[1].replace(')','')
        
#vaciar papelera        
print 'Vaciando papelera'
remote_conn.send('reset recycle-bin\n')
time.sleep(1)
OUTPUT = remote_conn.recv(5000).decode("utf-8")
if DEBUG: print OUTPUT
while True:
    time.sleep(1)
    if DEBUG: print 'Iteracion'
    if grep(OUTPUT, '[Y/N]'): 
        if DEBUG: print 'borrando'
        remote_conn.send('Y\n')
        time.sleep(1)
        OUTPUT = remote_conn.recv(5000).decode("utf-8")
        if DEBUG: print OUTPUT
    if grep(OUTPUT, PROMPT): break
    if grep(OUTPUT, 'empty'): break
    OUTPUT = remote_conn.recv(5000).decode("utf-8")
    if DEBUG: print OUTPUT
    
remote_conn.send('dir /all\n')
time.sleep(1)
OUTPUT = remote_conn.recv(5000).decode("utf-8")    
for line in OUTPUT.splitlines():
    if 'free' in line:
        print 'Espacio libre en flash: %s' % line.split('(')[1].replace(')','')

    
    
#actualizacion firmware
print 'Descargando imagen %s desde %s' % (FWFILE, TFTP_SERVER)
remote_conn.send('upgrade %s %s runtime\n' % (TFTP_SERVER,FWFILE))    
time.sleep(1)
OUTPUT = remote_conn.recv(5000).decode("utf-8")
if 'Overwrite' in OUTPUT:
    print 'La imagen ya existe. Salimos'
    remote_conn.send('N\n')
    remote_conn.close()
    exit(1)
elif 'Fail' in OUTPUT:
    print 'Fallo al descargar la imagen. Salimos'
    print OUTPUT
    remote_conn.send('N\n')
    remote_conn.close()
    exit(1)
    
while True:
    time.sleep(1)
    OUTPUT = remote_conn.recv(5000).decode("utf-8")
    #if DEBUG: print OUTPUT
    #if grep(OUTPUT, 'error'): break
    if (grep(OUTPUT, 'Failed') or grep(OUTPUT, 'error')): 
        print 'Fallo al descargar la imagen. Salimos'
        print OUTPUT
        remote_conn.send('N\n')
        remote_conn.close()
        exit(1)
    if grep(OUTPUT, 'reboot'): break
    sys.stdout.write("%s" % OUTPUT)
    sys.stdout.flush()

    
if DEBUG: print OUTPUT    
#salvar configuracion y reiniciar

if args.reboot:
    REBOOT= 'Y'
else:
    REBOOT = readAns('Reiniciar (Y/N): ')

if REBOOT == 'Y':
    remote_conn.send('save\n')
    time.sleep(5)
    OUTPUT = remote_conn.recv(1000).decode("utf-8")
    print OUTPUT
    if '[Y/N]' in OUTPUT: remote_conn.send('Y\n')
    time.sleep(1)
    OUTPUT = remote_conn.recv(1000).decode("utf-8")
    print OUTPUT
    remote_conn.send('\n')
    time.sleep(1)
    OUTPUT = remote_conn.recv(1000).decode("utf-8")
    print OUTPUT
    remote_conn.send('Y\n')
    while True:
        time.sleep(1)
        OUTPUT = remote_conn.recv(1000).decode("utf-8")
        if DEBUG: print OUTPUT
        if grep(OUTPUT, PROMPT): break
    
    print "Reiniciando"
    remote_conn.send('reboot\n')
    time.sleep(5)
    OUTPUT = remote_conn.recv(1000).decode("utf-8")
    print OUTPUT
    if '[Y/N]' in OUTPUT: remote_conn.send('Y\n')
    time.sleep(1)
    OUTPUT = remote_conn.recv(1000).decode("utf-8")
    print OUTPUT

remote_conn.close()