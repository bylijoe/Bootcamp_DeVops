#aerohive tools
import paramiko
import os
import sys
import time



def configBoot(ap):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print "conectando a %s" % ap
    try:
        ssh.connect(ap, username=USER, password=PASSWORD,timeout=2)
        shell = ssh.invoke_shell()
        time.sleep(1)
        res=shell.send('boot-param boot-file AP121.img.S\n')
        time.sleep(1)
        res=shell.send('boot-param netboot enable\n')
        time.sleep(1)
        res=shell.send('boot-param image-download enable\n')
        time.sleep(1)
        res=shell.send('boot-param server 192.168.252.100\n')
        time.sleep(1)
        shell.send('save config running current\n')
        ssh.close()
    except:
        print "No se puede establecer la conexion con %s" % ap

		
def hideSSID(ap):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print "conectando a %s" % ap
    try:
        ssh.connect(ap, username=USER, password=PASSWORD,timeout=2)
        shell = ssh.invoke_shell()
        time.sleep(2)
        print "SSID visible"
        shell.send('no ssid Vivacorporativo hide-ssid\n')
        print "sleep"
        time.sleep(2)
        print "Ocultando SSID"
        shell.send('ssid Vivacorporativo hide-ssid\n')
        time.sleep(2)
        shell.send('save config running current\n')
        ssh.close()
    except:
        print "No se puede establecer la conexion con %s" % ap
		
		
def flash(ap):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print "conectando a %s" % ap
    try:
        ssh.connect(ap, username=USER, password=PASSWORD,timeout=2)
        shell = ssh.invoke_shell()
        time.sleep(1)
        res=shell.send('show interface eth0 | include MAC\n')
        time.sleep(1)
        output = shell.recv(9000)
        for l in output.splitlines():
            if l.startswith('MAC addr'):
                mac=l.split(';')[0].split('=')[1]
            if l.startswith('AH-'):
                apHostname=l.split('#')[0]
        #print "Hostname: %s MAC: %s" % (apHostname, mac)
	print "Incio flash"
        for i in range(1,20):
            #print "Apagando el LED"
            res=shell.send('system led brightness off\n')
            time.sleep(0.31)
            #print "Encendiendo el LED"
            res=shell.send('system led brightness bright\n')
            time.sleep(0.31)
        ssh.close()
        ubicacion=raw_input('ubicacion?:')
        print "Hostname: %s\tMAC: %s\tUbicacion: %s" % (apHostname, mac, ubicacion)
    except:
        print "No se puede establecer la conexion con %s" % ap

def ledOff(ap):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print "conectando a %s" % ap
    try:
        ssh.connect(ap, username=USER, password=PASSWORD,timeout=2)
        shell = ssh.invoke_shell()
        time.sleep(1)
        res=shell.send('system led brightness off\n')
        ssh.close()
    except:
        print "No se puede establecer la conexion con %s" % ap

        
        
def ledOn(ap):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print "conectando a %s" % ap
    try:
        ssh.connect(ap, username=USER, password=PASSWORD,timeout=2)
        shell = ssh.invoke_shell()
        time.sleep(1)
        #print "Encendiendo el LED"
        res=shell.send('no system led power-saving-mode\n')
        if res==32:
            print 'Encendido'
            time.sleep(2)
            shell.send('save config running current\n')
        else:
            print 'Error'
        ssh.close()
    except:
        print "No se puede establecer la conexion con %s" % ap        

def resetDefault(ap):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print "conectando a %s" % ap
    try:
        ssh.connect(ap, username=USER, password=PASSWORD,timeout=2)
        shell = ssh.invoke_shell()
        time.sleep(1)
        res=shell.send('_reset press\n')
	ssh.close()
    except:
        print "No se puede establecer la conexion con %s" % ap

def countryCode(ap):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print "conectando a %s" % ap
    try:
        ssh.connect(ap, username=USER, password=PASSWORD,timeout=2)
        shell = ssh.invoke_shell()
        time.sleep(1)
        res=shell.send('boot-param region-code World\n')
        time.sleep(1)
        res=shell.send('boot-param country-code 724\n')
        time.sleep(2)
        res=shell.send('y\n')
	print "Reinicie el AP antes de cambiar el Country code: python resetDefault.py %s" %ap
        ssh.close()
    except:
        print "No se puede establecer la conexion con %s" % ap


USER = 'admin'
PASSWORD = 'mypassword'


