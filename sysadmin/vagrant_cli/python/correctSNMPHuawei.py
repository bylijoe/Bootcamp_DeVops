#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import paramiko
import getpass
import time
import sys

__author__ = 'Julian Garcia-Sotoca Pascual'


DEBUG = True

parser = argparse.ArgumentParser(description='Script para corregir parametros de snmp en switches')
parser.add_argument('-i','--ip',help='IP del switch', required=True)
parser.add_argument('-l','--location',help='ubicacion', required=True)
parser.add_argument('-c','--contact',help='Contacto', required=False)
args = parser.parse_args()



def expect(p,c):
    #c: conexion
    #p: prompt
    timeout = 10
    for tout in range(1,timeout):
        time.sleep(1)
        output = c.recv(1000).decode("utf-8")
        cur_prompt = output.strip()
        cur_prompt= cur_prompt.splitlines()
        cur_prompt=cur_prompt[len(cur_prompt)-1]
        if cur_prompt == p:
            return output

def readInt(m, max):
    #m: mensaje
    #max: opcion maxima
    print '[%d] %s' % (0, 'Exit')
    retries = 3
    for ret in range(0,retries):
        try:
            num = int(raw_input(m))
            if num in range(1,max+1):
                return num
            elif num == 0:
                break
            else:
                print 'Numero introducido no válido'
        except:
            print 'No ha introducido un número correcto'

def readAns(q):            
     while True:
        resp = raw_input(q).upper()
        if resp in ('Y', 'N'): 
            return resp
        else:
            print 'Respuesta no válida'
            
def grep(string, filter):
    fOut=[]
    for line in string.splitlines():
        if filter.upper() in line.upper(): 
            print line
            fOut.append(line)
    return fOut
    
def grepList(string, filter):
    fOut=[]
    for line in string.splitlines():
        if filter.upper() in line.upper(): 
            fOut.append(line)
    return fOut    

#ip = raw_input("Enter Host: ")
#username = raw_input("Enter Username: ")
#password = getpass.getpass()


ip = args.ip
if not args.contact: 
    contact = "Julian Garcia-Sotoca <sistemas@zafirohotels.com>"
else:
    contact =  args.contact
location = args.location


username = 'adminjgp'
password = 'ViVaHoTeLS'

remote_conn_pre = paramiko.SSHClient()
remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
remote_conn_pre.connect(ip, username=username, password=password, allow_agent=False, look_for_keys=False)
print ("SSH connection established to %s" % ip)
remote_conn = remote_conn_pre.invoke_shell()   
time.sleep(1)
output = remote_conn.recv(1000).decode("utf-8")

prompt = output.strip()
prompt= prompt.splitlines()
prompt=prompt[-1]
if DEBUG: print prompt
if DEBUG: print output


#remote_conn.send('terminal length 0\n')
#time.sleep(1)
#output = remote_conn.recv(1000).decode("utf-8")
remote_conn.send('dis ver\n')
time.sleep(1)
output = remote_conn.recv(5000).decode("utf-8")

#for o in output:
#    if o.startswith('VRP'): print o.split(', ')[1]
#print grepList(output, 'vrp')[0]    
print 'Current version: %s' % grepList(output, 'vrp')[0].split()[-1].replace(')','')
swModel=grepList(output, 'uptime')[0].split()[1] 
print 'Model: %s' %  swModel

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
remote_conn.send('quit\n')
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
    
        
remote_conn.close()

