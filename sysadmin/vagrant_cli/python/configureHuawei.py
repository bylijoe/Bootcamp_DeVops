#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paramiko
import getpass
import time
import sys
import socket
import argparse
from swtools import grepList, huaweiConnect

__author__ = 'Xisco Chacon'

parser = argparse.ArgumentParser(description='Script para corregir parametros de configuración en switches')
parser.add_argument('-i','--ip',help='IP del switch', required=True)
parser.add_argument('-d','--switch_debug',type=bool, default=False, help='Modo Debug')

args = parser.parse_args()

ip = args.ip
#print ip

DEBUG=args.switch_debug
#print DEBUG

def sendCommand(rem_con, command, t=1):
    remote_conn.send(command+'\n') 
    time.sleep(t)
    out = remote_conn.recv(5000).decode("utf-8")
    if DEBUG: print out
    return out
 
remote_conn_pre = huaweiConnect(ip)
remote_conn = remote_conn_pre.invoke_shell()   
time.sleep(1)
output = remote_conn.recv(1000).decode("utf-8")

prompt = output.strip()
prompt= prompt.splitlines()
prompt=prompt[-1].replace('<','').replace('>','')

if DEBUG: print 'prompt: '+prompt
if DEBUG: print output

print 'Configuring Switch %s' % prompt

#pasar a system-view y modificar configuracion
output = sendCommand(remote_conn, 'sys')
output = sendCommand(remote_conn, 'header shell information "Propiedad de Zafiro Hotels"')
output = sendCommand(remote_conn, 'header login information "Sistema monitorizado <sistemas@zafirohotels.com>"')
output = sendCommand(remote_conn, 'aaa')
output = sendCommand(remote_conn, 'local-user admin password irreversible-cipher ZafiroHotels17!')
output = sendCommand(remote_conn, 'local-user admin privilege level 15')
if '[Y/N]' in output: sendCommand(remote_conn, 'Y')
output = sendCommand(remote_conn, 'local-user admin service-type ssh http')
output = sendCommand(remote_conn, 'local-user adminzfr password irreversible-cipher ZafiroHotels17!')
output = sendCommand(remote_conn, 'local-user adminzfr privilege level 15')
if '[Y/N]' in output: sendCommand(remote_conn, 'Y')
output = sendCommand(remote_conn, 'local-user adminzfr service-type ssh http')
output = sendCommand(remote_conn, 'q')
output = sendCommand(remote_conn, 'stelnet server enable')
output = sendCommand(remote_conn, 'ssh user admin')
output = sendCommand(remote_conn, 'ssh user admin authentication-type password')
output = sendCommand(remote_conn, 'ssh user admin service-type stelnet')
output = sendCommand(remote_conn, 'ssh user adminzfr')
output = sendCommand(remote_conn, 'ssh user adminzfr authentication-type password')
output = sendCommand(remote_conn, 'ssh user adminzfr service-type stelnet')
output = sendCommand(remote_conn, 'ssh client first-time enable')
output = sendCommand(remote_conn, 'q')

#SNMP
output = sendCommand(remote_conn, 'snmp-agent')
output = sendCommand(remote_conn, 'snmp-agent community read cipher ZafiroHotels1')
output = sendCommand(remote_conn, 'snmp-agent sys-info contact Xisco Chacon')
output = sendCommand(remote_conn, 'snmp-agent sys-info version v1 v3')

#salvar configuracion
print 'save'
output = sendCommand(remote_conn, 'save', 3)
output = sendCommand(remote_conn, 'y')
print 'tftp'
output = sendCommand(remote_conn, 'ping 192.168.0.62 ', 5)
output = sendCommand(remote_conn, 'tftp 192.168.0.62 put vrpcfg.zip %s.zip' % prompt, 5)

#remote_conn.send('tftp 192.168.0.62 put vrpcfg.zip %s.zip\n' % prompt) 
#time.sleep(3)
#output = remote_conn.recv(5000).decode("utf-8")
#if DEBUG: print output

remote_conn.close()