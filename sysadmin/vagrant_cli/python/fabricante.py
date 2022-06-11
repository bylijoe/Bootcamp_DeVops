#!/usr/bin/env python
# -*- coding: utf-8 -*-

import netsnmp
import argparse
import paramiko
import getpass
import time
import sys

__author__ = 'Xisco Chacon'

parser = argparse.ArgumentParser(description='Script para corregir parametros de configuración en switches')
parser.add_argument('-i','--ip',help='IP del switch', required=True)
args = parser.parse_args()

DEBUG = False

def getVendor(ip):
    parametros = {
            "Version": 1,
            "DestHost": ip,
            "Community": "V1vaH0tels"
        }

    vendor=netsnmp.snmpget(netsnmp.Varbind("SNMPv2-MIB::sysDescr.0"), **parametros)[0]
    if DEBUG: print vendor

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
        return vendor


ip = args.ip

v = getVendor(ip)
print v