#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paramiko
import getpass
import time
import sys

DEBUG = False

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

ip = raw_input("Enter Host: ")
#username = raw_input("Enter Username: ")
#password = getpass.getpass()

FTP_SERVER='192.168.252.100'
FTP_USER='huawei'
FTP_PASS='iewauh16'
#ip = '172.17.3.11'
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

if swModel == 'S5700-10P-PWR-LI-AC':
    FTP_PATH='S5700-10P-LI'
elif swModel == 'S5700-28P-PWR-LI-AC':
    FTP_PATH='S5700-P-LI'
elif swModel == 'S5700-28X-PWR-LI-AC':    
    FTP_PATH='S5700-X-LI'
elif swModel == 'S5700-52X-PWR-LI-AC':    
    FTP_PATH='S5700-X-LI'
elif swModel == 'S5710-28C-PWR-EI':    
    FTP_PATH='S5710-EI'    
else:
    print 'modelo no registrado'
    exit(1)
  
if DEBUG: print output

print '\nEstableciendo conexion FTP'
print 'FTP_PATH: %s' % FTP_PATH
remote_conn.send('ftp %s\n' % FTP_SERVER)
time.sleep(2)
output = remote_conn.recv(5000).decode("utf-8")
if DEBUG: print output
remote_conn.send('%s\n' % FTP_USER)
time.sleep(2)
output = remote_conn.recv(5000).decode("utf-8")
if DEBUG: print output
remote_conn.send('%s\n' % FTP_PASS)
time.sleep(2)
output = remote_conn.recv(5000).decode("utf-8")
if DEBUG: print output

grep(output, '230')
print output

ftp_prompt = output.strip()
ftp_prompt= ftp_prompt.splitlines()
ftp_prompt=ftp_prompt[-1]

remote_conn.send('cd %s\n' % FTP_PATH)
time.sleep(2)
output = remote_conn.recv(5000).decode("utf-8")
if DEBUG: print output

remote_conn.send('mget *.cc *.web.7z *.pat\n')
print 'Descargando ficheros'
#remote_conn.send('mget *.pat\n')
#time.sleep(2)
#output = remote_conn.recv(5000).decode("utf-8")
#print output
#if '[Y/N]' in output: remote_conn.send('Y\n')


while True:
    time.sleep(1)
    output = remote_conn.recv(1000).decode("utf-8")
    if DEBUG: print output
    grep(output, 'error')
    grep(output, '226')
    grep(output,'150')
    if '%' in output.splitlines()[-1]:
        sys.stdout.write("\r%s" % output.splitlines()[-1])
        sys.stdout.flush()

    
    #print output
    if '[Y/N]' in output: remote_conn.send('Y\n')
    ftp_prompt = output.strip()
    ftp_prompt= ftp_prompt.splitlines()
    ftp_prompt=ftp_prompt[-1]
    if ftp_prompt == '[ftp]':
        remote_conn.send('quit\n')
        time.sleep(1)
        output = remote_conn.recv(5000).decode("utf-8")
        grep(output, 'Goodbye')
        if DEBUG: print output
        #print output
        break

remote_conn.send('dir *.cc\n')
time.sleep(2)
output = remote_conn.recv(5000).decode("utf-8")

print '\nconfigurando Arranque'
print 'Software'
i=0
s={}
p={}
for l in output.splitlines():
    if '.cc' in l and not 'dir' in l:
        i=i+1
        s[i]=l.split()[-1]
        print '[%d] %s' % (i, s[i])

#soft = int(raw_input('Que version de software configurar: '))
i=i+1
print '[%d] %s' % (i, 'No Cambiar')
soft = readInt('Que version de software configurar: ', i)
try:
    if soft == i:
        print 'No se modifica el software actual'
    else:            
        print 'Software configurado: %s' % s[soft]    
        remote_conn.send('startup system-software %s\n' % s[soft] )        
        output = expect(prompt, remote_conn)
        grep(output,'info')
except:
    print 'Salida'
    sys.exit()
        
        
#print output


#time.sleep(10)

#output = remote_conn.recv(5000).decode("utf-8")

#print output

print '\nParche'
remote_conn.send('dir *.pat\n')
time.sleep(2)
output = remote_conn.recv(5000).decode("utf-8")
i=0

for l in output.splitlines():
    if '.pat' in l and not 'dir' in l: 
        i=i+1
        p[i]=l.split()[-1]
        print '[%d] %s' % (i, p[i])
      

#patch = int(raw_input('Que version de parche configurar: '))
i=i+1
print '[%d] %s' % (i, 'No Cambiar')
patch = readInt('Que version de parche configurar: ',i)
try: 
    if patch == i:
        print 'No se modifica el parche actual'
    else:
        print 'Parche configurado: %s' % p[patch]
        remote_conn.send('startup patch %s\n' % p[patch])
        output = expect(prompt, remote_conn)        
        grep(output,'info')
except:
    print 'Salida'
    sys.exit()
        
        

#time.sleep(10)
#output = remote_conn.recv(5000).decode("utf-8")
#print output


print '\nConfiguracion guardada'
remote_conn.send('dis startup\n')        
time.sleep(1)
output = remote_conn.recv(5000).decode("utf-8")
if DEBUG: print output
grep(output, 'flash')


#reboot = raw_input('Reiniciar (Y/N): ')
reboot = readAns('Reiniciar (Y/N): ')
if reboot == 'Y':
    remote_conn.send('save\n')
    time.sleep(5)
    output = remote_conn.recv(1000).decode("utf-8")
    print output
    if '[Y/N]' in output: remote_conn.send('Y\n')
    remote_conn.send('reboot\n')
    time.sleep(10)
    output = remote_conn.recv(1000).decode("utf-8")
    print output
    if '[Y/N]' in output: remote_conn.send('Y\n')
        
remote_conn.close()

