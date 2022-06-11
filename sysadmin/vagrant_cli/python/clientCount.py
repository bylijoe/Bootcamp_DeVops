#!/usr/bin/env python
import argparse
import netsnmp
import sys
import datetime
import time
import random

def countClients(ip):
    parametros = {
        "Version": 1,
        "DestHost": ip,
        "Community": "V1vaH0tels"
    }
    
    #iso.3.6.1.2.1.1.5.0 = STRING: "AH-322e40"
    #iso.3.6.1.2.1.1.6.0 = STRING: "Marketing@Oficina"
    l=0
    for j in range(1,3):
        if l==0:
            l=len(netsnmp.snmpwalk(netsnmp.Varbind(".1.3.6.1.4.1.26928.1.1.1.2.1.2.1.3"), **parametros))
            if l==0:
                time.sleep(random.random()*j)
            
    hostname=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.5.0"), **parametros)[0]
    location=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.6.0"), **parametros)[0]
    timestamp=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    print "%s;%s;%s;%s;%s" % (timestamp,hostname,ip,location,l)
    

__author__ = 'Julian Garcia-Sotoca Pascual'

parser = argparse.ArgumentParser(description='Script para obtener el listado de clientes conectados en listado de APs')
parser.add_argument('-l','--list',help='List', required=True)
args = parser.parse_args()

listaAPs=args.list

if 'lst' in listaAPs:
    apList=open(listaAPs)
    print "%s;%s;%s;%s;%s" % ('Hora','AP','IP', 'Ubicacion','Clientes')
    while True:
        ip = apList.readline().replace('\n','')
        if not ip: break
        countClients(ip)
else:
    print 'Debes pasar un archivo con extension .lst'
    exit()


exit()

