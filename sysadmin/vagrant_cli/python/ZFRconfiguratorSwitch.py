#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import paramiko
import getpass
import time
import sys

__author__ = 'Xisco Chacon'

parser = argparse.ArgumentParser(description='Script para corregir parametros de configuración en switches - HP o HUAWEI')
parser.add_argument('-i','--ip',help='IP del switch', required=True)
args = parser.parse_args()

DEBUG = False

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
 
ip = args.ip
#print ip

username = 'adminjgp'
password = ''
try:
	remote_conn_pre = paramiko.SSHClient()
	remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())     
	remote_conn_pre.connect(ip, username=username, password=password, allow_agent=False, look_for_keys=False, timeout=5)
except paramiko.AuthenticationException:
	if DEBUG: print "Error autenticacion"
	try:
		remote_conn_pre.connect(ip, username=username, password='PASSWORD', allow_agent=False, look_for_keys=False, timeout=5)
	except:
		try:
			remote_conn_pre.connect(ip, username=username, password='PASSWORD/', allow_agent=False, look_for_keys=False, timeout=5)
		except:
			try:
				remote_conn_pre.connect(ip, username=username, password='PASSWORD!', allow_agent=False, look_for_keys=False, timeout=5)
			except:
				print "%s: Error de autenticacion" % ip
				sys.exit(1)
    

print ("SSH connection established to %s" % ip)
remote_conn = remote_conn_pre.invoke_shell()   
time.sleep(1)
output = remote_conn.recv(1000).decode("utf-8")

prompt = output.strip()
prompt= prompt.splitlines()
prompt=prompt[-1].replace('<','').replace('>','')

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