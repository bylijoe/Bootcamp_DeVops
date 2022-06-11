#!/usr/bin/env python
import paramiko
import os
import sys
import time
import argparse
import random
import netsnmp

USER = 'admin'
PASSWORD = 'HotelsVIVA'
WAIT = 0.1


def printValidOptions():
    parser.error('''Opcion no valida. Opciones permitidas:
        airtime
        tx_airtime
        rx_airtime
        crc_airtime
        utilization
        tx_utilization 
        rx_utilization 
        int_utilization
        client_count
    ''')

def runCommand(h,c, interface):

    if 'airtime' in c:
        if not interface: 
            #print 'Es necesario especificar una interfaz'
            #parser.print_help()
            parser.error('Es necesario especificar una interfaz con la opcion %s' % c)
        command='show interface %s | include airtime' % interface
        param='airtime'
    elif 'utilization' in c:
        if not interface: 
            parser.error('Es necesario especificar una interfaz con la opcion %s' % c)
        command='show interface %s | include utilization' % interface
        param='utilization'
    elif 'client_count' in c:
        parametros = {
            "Version": 1,
            "DestHost": h,
            "Community": "V1vaH0tels",
            "Timeout": 5000000,
            "Retries": 3 
        }
        l=len(netsnmp.snmpwalk(netsnmp.Varbind(".1.3.6.1.4.1.26928.1.1.1.2.1.2.1.3"), **parametros))
        print l
        exit(0)
    else:
        #print 'invalid command'
        printValidOptions()
        exit(1)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #print "conectando a %s" % h
    try:
        ssh.connect(h, username=USER, password=PASSWORD,timeout=WAIT)
        #print 'conectado'
        
    except:
        print "No se puede establecer la conexion con %s" % h
        exit(1)
    #print 'shell'
    shell = ssh.invoke_shell()
    time.sleep(WAIT)
    #print 'wait'
    res=shell.send(command+'\n')
    #print 'send: '+command
    time.sleep(WAIT)
    #print 'wait'
    command_output = shell.recv(9000)
    #print 'output'
    #print command_output
    for l in command_output.splitlines():
        #print 'output: '+l
        if param in l and '%' in l:
            #print 'entra'
            if c=='tx_airtime': print l.split(';')[0].split('=')[1].replace('%','')
            elif c=='rx_airtime': print l.split(';')[1].split('=')[1].replace('%','')
            elif c=='crc_airtime': print l.split(';')[2].split('=')[1].replace('%','')
            elif c=='airtime': print l
            elif c=='tx_utilization': print l.split(';')[0].split('=')[1].replace('%','')
            elif c=='rx_utilization': print l.split(';')[1].split('=')[1].replace('%','')
            elif c=='int_utilization': print l.split(';')[2].split('=')[1].replace('%','')
            elif c=='utilization': print l
            else: printValidOptions()
            #print 'line: '+l
    ssh.close()
    

__author__ = 'Julian Garcia-Sotoca Pascual'

parser = argparse.ArgumentParser(description='Script para el analisis de logs de dispositivos de red', conflict_handler='resolve')
parser.add_argument('-h','--host', help='AP donde nos vamos a conectar',required=True)
parser.add_argument('-c','--command',help='comando a ejecutar', required=True)
parser.add_argument('-i','--interface',help='interfaz a consultar', required=False)
args = parser.parse_args()


runCommand(args.host, args.command, args.interface)
exit(0)
