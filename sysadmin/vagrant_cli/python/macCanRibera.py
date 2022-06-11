#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import time
import syslog


SWITCH_IP="172.16.28.2"
#SWITCH_IP="10.28.0.2"
#May 17 12:42:00 sv240dhcp dhcpd: DHCPACK on 10.26.30.195 to 4c:57:ca:15:d6:7c (Nadia) via 10.26.0.1


command='snmpwalk -c ZafiroHotels1 -v1 %s -OXsq .1.3.6.1.2.1.3.1.1.2' % SWITCH_IP
try:
    result = subprocess.check_output(command.split())

except:
    print "Problema al ejecutar el snmpwalk"
    exit(1)

for l in result.splitlines():
    if "10.28." in l:
        IP='.'.join(l.split(' \"')[0].split('.')[-4:])
        MAC=':'.join(l.split(' \"')[1].split())
        currTime=(time.strftime("%b %d %H:%M:%S"))
        #print "IP=%s MAC=%s" % ('.'.join(IP),':'.join(MAC))
        #print "IP=%s MAC=%s" % (IP,MAC)
        #print "%s sv240dhcp dhcpd: DHCPACK on %s to %s (Unknown) via localhost" % (currTime,IP,MAC)
        syslog.openlog(facility=syslog.LOG_LOCAL6)
        syslog.syslog("DHCPACK on %s to %s (Unknown) via localhost" % (IP,MAC))
