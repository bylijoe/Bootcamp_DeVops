#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paramiko
import getpass
import time
import sys
import socket
import netsnmp
import argparse

DEBUG = False

def grepList(string, filter):
    fOut=[]
    for line in string.splitlines():
        if filter.upper() in line.upper(): 
            fOut.append(line)
    return fOut    
    
    

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
                print 'Numero introducido no v�lido'
        except:
            print 'No ha introducido un n�mero correcto'
            
            
def readAns(q):            
     while True:
        resp = raw_input(q).upper()
        if resp in ('Y', 'N'): 
            return resp
        else:
            print 'Respuesta no v�lida'

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
    
def hpConnect(sw):
    username = 'admin'
    #password = getpass.getpass()
    hoteles = { '17.1' : 'club',
                '17.2' : 'resort',
                '17.3' : 'suite',
                '16.3' : 'tropic',
                '16.4' : 'golf',
                '16.5' : 'sunrise',
                '16.6' : 'palmanova',
                '16.8' : 'bahia',
                '16.11' : 'picafort',
                '16.12' : 'menorca',
                '16.14' : 'blue',
                '16.19' : 'mallorca',
                '16.22' : 'edenlago',
                '16.23' : 'binibeca',
                '16.25' : 'rey',
                '16.26' : 'zafiro',
    }
    password = 'W'+ hoteles['.'.join(sw.split('.')[1:3])] + '01'
    
    try:
        remote_conn_pre = paramiko.SSHClient()
        remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())     
        remote_conn_pre.connect(sw, username=username, password=password, allow_agent=False, look_for_keys=False, timeout=5)
    except paramiko.AuthenticationException:
        if DEBUG: print "Error autenticacion"
        try:
            remote_conn_pre.connect(sw, username=username, password='PASSWORD', allow_agent=False, look_for_keys=False, timeout=5)
        except:
            try:
                remote_conn_pre.connect(sw, username=username, password='PASSWORD', allow_agent=False, look_for_keys=False, timeout=5)
            except:
                try:
                    remote_conn_pre.connect(sw, username=username, password='PASSWORD', allow_agent=False, look_for_keys=False, timeout=5)
                except:
                    print "%s: Error de autenticacion" % sw
                    sys.exit(1)
    except socket.timeout:
        print "%s: Error de conexion" % sw
        sys.exit(1)
    except:
        print "%s: Error no esperado" % sw
        sys.exit(1)
    return remote_conn_pre
    
def huaweiConnect(sw):
    username = 'admin'
    password = 'ZafiroHotels17!'
    hoteles = { '17.1' : 'club',
                '17.2' : 'resort',
                '17.3' : 'suite',
                '16.3' : 'tropic',
                '16.4' : 'golf',
                '16.5' : 'sunrise',
                '16.6' : 'palmanova',
                '16.8' : 'bahia',
                '16.11' : 'picafort',
                '16.12' : 'menorca',
                '16.14' : 'blue',
                '16.19' : 'mallorca',
                '16.22' : 'edenlago',
                '16.23' : 'binibeca',
                '16.25' : 'rey',
                '16.26' : 'zafiro',
    }

    try:
        remote_conn_pre = paramiko.SSHClient()
        remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())     
        remote_conn_pre.connect(sw, username=username, password=password, allow_agent=False, look_for_keys=False, timeout=5)
    except paramiko.AuthenticationException:
        if DEBUG: print "Error autenticacion"
        try:
            remote_conn_pre.connect(sw, username=username, password='PASSWORD', allow_agent=False, look_for_keys=False, timeout=5)
        except:
            try:
                remote_conn_pre.connect(sw, username=username, password='PASSWORD=', allow_agent=False, look_for_keys=False, timeout=5)
            except:
                try:
                    print "%s: Error de autenticacion %s" % sw,username
                    username = 'adminjgp'
                    
                    password = 'W'+ hoteles['.'.join(sw.split('.')[1:3])] + '01'
                    remote_conn_pre.connect(sw, username=username, password='PASSWORD', allow_agent=False, look_for_keys=False, timeout=5)
                except:
                    try:
                        remote_conn_pre.connect(sw, username=username, password='PASSWORD', allow_agent=False, look_for_keys=False, timeout=5)
                    except:
                        try:
                            remote_conn_pre.connect(sw, username=username, password='PASSWORD!', allow_agent=False, look_for_keys=False, timeout=5)
                        except:
                            print "%s: Error de autenticacion %s" % sw,username
                            sys.exit(1)
    except socket.timeout:
        print "%s: Error de conexion" % sw
        sys.exit(1)
    except:
        print "%s: Error no esperado" % sw
        sys.exit(1)
    return remote_conn_pre

    
def getHPver(c):
    c.send('summary\n')
    c.send(' ')
    time.sleep(1)
    output = c.recv(5000).decode("utf-8")
    if DEBUG: print output
    if 'uptime' in output:
        sw_ver=grepList(output, 'Release')[0].split()[-1].replace(')','')
        swModel=grepList(output, 'uptime')[0].split('uptime')[0] 
        return (swModel,sw_ver)
    else:
        print '%s Switch no HP' % sw

def getVendor(ip):
    parametros = {
            "Version": 1,
            "DestHost": ip,
            "Community": "V1vaH0tels"
        }

    vendor=netsnmp.snmpget(netsnmp.Varbind("SNMPv2-MIB::sysDescr.0"), **parametros)[0]

    if DEBUG: print vendor

    if not (vendor == None):
        if "hpe" in vendor.lower():
            model=vendor.split()[1]
            release=vendor.split()[7]
            print "Modelo: %s - Firmware %s" % (model,release)
            return "HP"
        elif "huawei" in vendor.lower():
            model=vendor.split()[0]
            release=vendor.split()[11].replace(")","")
            print "Modelo: %s - Firmware %s" % (model,release)
            return "Huawei"
        else:
            return "SN/SC"
    
    parametros = {
        "Version": 1,
        "DestHost": ip,
        "Community": "ZafiroHotels"
    }

    vendor=netsnmp.snmpget(netsnmp.Varbind("SNMPv2-MIB::sysDescr.0"), **parametros)[0]

    if DEBUG: print vendor

    if not (vendor == None):
        if "hpe" in vendor.lower():
            model=vendor.split()[1]
            release=vendor.split()[7]
            print "Modelo: %s - Firmware %s" % (model,release)
            return "HP"
        elif "huawei" in vendor.lower():
            model=vendor.split()[0]
            release=vendor.split()[11].replace(")","")
            print "Modelo: %s - Firmware %s" % (model,release)
            return "Huawei"
        else:
            return "SN/SC"

    parametros = {
        "Version": 1,
        "DestHost": ip,
        "Community": " "
    }

    vendor=netsnmp.snmpget(netsnmp.Varbind("SNMPv2-MIB::sysDescr.0"), **parametros)[0]

    if DEBUG: print vendor

    if not (vendor == None):
        if "hpe" in vendor.lower():
            model=vendor.split()[1]
            release=vendor.split()[7]
            print "Modelo: %s - Firmware %s" % (model,release)
            return "HP"
        elif "huawei" in vendor.lower():
            model=vendor.split()[0]
            release=vendor.split()[11].replace(")","")
            print "Modelo: %s - Firmware %s" % (model,release)
            return "Huawei"
        else:
            return "SN/SC"

