#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paramiko
import getpass
import time
import sys
import argparse
from swtools import grepList, hpConnect

DEBUG = True

__author__ = 'Julian Garcia-Sotoca Pascual'
parser = argparse.ArgumentParser(description='Script para actualizar el firmware de un switch HP')
parser.add_argument('-i','--switch_ip',help='IP del switch definido en Pandora', required=True)
parser.set_defaults(reboot=False)
args = parser.parse_args()

#ip = raw_input("Enter Host: ")
ip=args.switch_ip


def sendCommand(rem_con, command, t=1):
    remote_conn.send(command+'\n') 
    time.sleep(t)
    out = remote_conn.recv(5000).decode("utf-8")
    if DEBUG: print out
    return out

remote_conn_pre = hpConnect(ip)
remote_conn = remote_conn_pre.invoke_shell()   
time.sleep(1)
output = remote_conn.recv(1000).decode("utf-8")

prompt = output.strip()
prompt= prompt.splitlines()
prompt=prompt[-1].replace('<','').replace('>','')

if DEBUG: print 'prompt: '+prompt
if DEBUG: print output

#obtener version
remote_conn.send('summary\n')
remote_conn.send(' ')
time.sleep(1)
output = remote_conn.recv(5000).decode("utf-8")
#if DEBUG: print output

swModel = grepList(output, 'uptime')[0].split('uptime')[0] 

print "Modelo: %s" % swModel

#pasar a modo avanzado:
if ('1910' or 'Baseline') in swModel:
    SYSPASSWD = '512900'
elif '1920' in swModel:
    SYSPASSWD = 'Jinhua1920unauthorized'
else:
    print 'Modelo no especificado. Salimos'
    exit(1)

output = sendCommand(remote_conn, '_cmdline-mode on')
output = sendCommand(remote_conn, 'Y')
time.sleep(1)
output = sendCommand(remote_conn, '%s' % SYSPASSWD)
	
#pasar a system-view y modificar configuracion
output = sendCommand(remote_conn, 'sys')
output = sendCommand(remote_conn, 'local-user admin')
output = sendCommand(remote_conn, 'password cipher ZafiroHotels17!')
output = sendCommand(remote_conn, 'service-type ftp')
output = sendCommand(remote_conn, 'service-type lan--access')
output = sendCommand(remote_conn, 'service-type portal')
output = sendCommand(remote_conn, 'service-type ssh')
output = sendCommand(remote_conn, 'service-type telnet')
output = sendCommand(remote_conn, 'service-type terminal')
output = sendCommand(remote_conn, 'service-type web')
output = sendCommand(remote_conn, 'quit')
output = sendCommand(remote_conn, 'local-user adminzfr')
output = sendCommand(remote_conn, 'password cipher ZafiroHotels17!')
output = sendCommand(remote_conn, 'service-type ftp')
output = sendCommand(remote_conn, 'service-type lan--access')
output = sendCommand(remote_conn, 'service-type portal')
output = sendCommand(remote_conn, 'service-type ssh')
output = sendCommand(remote_conn, 'service-type telnet')
output = sendCommand(remote_conn, 'service-type terminal')
output = sendCommand(remote_conn, 'service-type web')
output = sendCommand(remote_conn, 'authorization-attribute level 3')
output = sendCommand(remote_conn, 'quit')
output = sendCommand(remote_conn, 'quit')

#salvar configuracion
print 'save'
output = sendCommand(remote_conn, 'save', 3)
if '[Y/N]' in output: sendCommand(remote_conn, 'Y')
output = sendCommand(remote_conn, '')
output = sendCommand(remote_conn, '\n')
if '[Y/N]' in output: sendCommand(remote_conn, 'Y')
print 'tftp'
output = sendCommand(remote_conn, 'tftp 192.168.0.62 put startup.cfg %s.cfg' % prompt, 5)
output = sendCommand(remote_conn, 'tftp 192.168.0.62 put %s.cfg %s.cfg' % (prompt,prompt), 5)

remote_conn.close()