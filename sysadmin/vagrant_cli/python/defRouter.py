#!/usr/bin/env python
import argparse
import netsnmp
import sys

def query_yes_no(question, default="yes"):
    valid = {"yes":True, "y":True, "ye":True, "no":False, "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " 
                             "(or 'y' or 'n').\n")

__author__ = 'Julian Garcia-Sotoca Pascual'

parser = argparse.ArgumentParser(description='Script para crear la monitorizacion de un router en pandora')
parser.add_argument('-r','--router',help='Nombre del router definido en Pandora', required=True)
parser.add_argument('-i','--router_ip',help='IP del router definido en Pandora', required=True)
args = parser.parse_args()

router=args.router
router_ip=args.router_ip

parametros = {
    "Version": 1,
    "DestHost": router_ip,
    "Community": "V1vaH0tels"
}

output=''
for idx in netsnmp.snmpwalk(netsnmp.Varbind("IF-MIB::ifIndex"),
**parametros):
    #print idx
    description= netsnmp.snmpget(netsnmp.Varbind("IF-MIB::ifDescr", idx),
                 **parametros)
    if (description[0].startswith('ge') or description[0].startswith('fe') or description[0].startswith('Gi')) and description[0].find('.')<1:
        #print description[0]
        if query_yes_no('generar configuracion para %s' % description[0]):
            output=output+"perl pandora_manage.pl /etc/pandora/pandora_server.conf --create_snmp_module 'ifInOctets_%s'  remote_snmp_inc '%s' %s 161 1 V1vaH0tels .1.3.6.1.2.1.2.2.1.10.%s 'In Octets %s' 'Networking' 0 0\n" % (description[0], router, router_ip, idx, description[0])
            output=output+"perl pandora_manage.pl /etc/pandora/pandora_server.conf --create_snmp_module 'ifOutOctets_%s' remote_snmp_inc '%s' %s 161 1 V1vaH0tels .1.3.6.1.2.1.2.2.1.16.%s 'Out Octets %s' 'Networking' 0 0\n" % (description[0], router, router_ip, idx, description[0])
            output=output+"perl pandora_manage.pl /etc/pandora/pandora_server.conf --create_snmp_module 'ifInErrors_%s'  remote_snmp_inc '%s' %s 161 1 V1vaH0tels .1.3.6.1.2.1.2.2.1.14.%s 'In Errors %s' 'Networking' 0 0\n" % (description[0], router, router_ip, idx, description[0])
            output=output+"perl pandora_manage.pl /etc/pandora/pandora_server.conf --create_snmp_module 'ifOutErrors_%s' remote_snmp_inc '%s' %s 161 1 V1vaH0tels .1.3.6.1.2.1.2.2.1.20.%s 'Out Errors %s' 'Networking' 0 0\n" % (description[0], router, router_ip, idx, description[0])
            output=output+"perl pandora_manage.pl /etc/pandora/pandora_server.conf --create_snmp_module 'ifDescr_%s'     remote_snmp_string '%s' %s 161 1 V1vaH0tels .1.3.6.1.2.1.2.2.1.2.%s 'If Description %s' 'Networking' 0 0\n" % (description[0], router, router_ip, idx, description[0])
#            output=output+"perl pandora_manage.pl /etc/pandora/pandora_server.conf --update_module 'ifInOctets_%s'  '%s' module_group 'Networking'\n" % (description[0], router)
#            output=output+"perl pandora_manage.pl /etc/pandora/pandora_server.conf --update_module 'ifOutOctets_%s' '%s' module_group 'Networking'\n" % (description[0], router)
#            output=output+"perl pandora_manage.pl /etc/pandora/pandora_server.conf --update_module 'ifInErrors_%s'  '%s' module_group 'Networking'\n" % (description[0], router)
#            output=output+"perl pandora_manage.pl /etc/pandora/pandora_server.conf --update_module 'ifOutErrors_%s' '%s' module_group 'Networking'\n" % (description[0], router)
#            output=output+"perl pandora_manage.pl /etc/pandora/pandora_server.conf --update_module 'ifDescr_%s'     '%s' module_group 'Networking'\n" % (description[0], router)


print output
