#!/usr/bin/env python
import argparse
import netsnmp
import sys
import datetime
import numpy


__author__ = 'Julian Garcia-Sotoca Pascual'

parser = argparse.ArgumentParser(description='Script parsear el fichero de clientes conectados')
parser.add_argument('-c','--code',help='Codigo de hotel a mostrar', required=True)
parser.add_argument('-d','--day',help='dia que se quiere parsear. Formato 2016-06-10', required=True)
args = parser.parse_args()

code=args.code
day=args.day

if code == '1':
    APList=['AH-527080', 'AH-18cd80', 'AH-90d300', 'AH-009340', 'AH-8ed880']
elif code == '2':
    APList=['AH-007440', 'AH-cdaec0',  'AH-768480', 'AH-768600', 'AH-76a200', 'AH-cbbdc0', 
            'AH-cbd900', 'AH-cc1380', 'AH-cd4f40', 'AH-cd7580', 'AH-cd9e00', 'AH-cbd6c0', 'AH-ecc480', 'AH-7f66c0']
elif code == '3':
    APList=['AH-8ea940', 'AH-0826c0', 'AH-8f1dc0', 'AH-8ed880',  'AH-5dc300', 'AH-5dd280', 'AH-7f8300']
elif code == '4':
    APList=['AH-008280', 'AH-00ca80', 'AH-22b880', 'AH-5db480', 'AH-5dbac0', 'AH-5dd740', 'AH-5ddc00']  
elif code == '5':
    APList=['AH-768bc0', 'AH-768e40', 'AH-769900', 'AH-cbc080', 'AH-cbc1c0', 'AH-cd0240', 'AH-cd36c0', 'AH-cd52c0']
elif code == '6':
    APList=['AH-2c0940', 'AH-83f940', 'AH-840400', 'AH-cc2140', 'AH-cc2500', 'AH-cc3ec0', 'AH-cd4540']    
elif code == '8':
    APList=['AH-7fad40', 'AH-8f4040', 'AH-8f3480', 'AH-8f3f80', 'AH-00b0c0', 'AH-cc3ac0', 'AH-cc4940', 'AH-cbc3c0', 'AH-cbd700']
elif code == '11':
    APList=['AH-9102c0', 'AH-910ac0', 'AH-913f00', 'AH-7f9300', 'AH-913ec0', 'AH-7f9040']    
elif code == '15':
    APList=['AH-768dc0', 'AH-76ae00', 'AH-cda100', 'AH-cda6c0']    
elif code == '16':
    APList=['AH-007640', 'AH-008200', 'AH-009600', 'AH-5d8280', 'AH-5dcc80', 'AH-5dda80', 'AH-5ddb40', 'AH-5dde40']    
elif code =='19':
    APList=['AH-cbc9c0',	'AH-914d00',	'AH-90bc40',	'AH-cc0940',	'AH-cc0d00']
elif code =='26':
    APList=['AH-76a340', 'AH-769200', 'AH-768240', 'AH-76a240', 'AH-cbf6c0', 'AH-cbba80', 'AH-cd0fc0', 
            'AH-cbbe40', 'AH-cd8200', 'AH-cbf680', 'AH-cbfc00', 'AH-cd4180', 'AH-cbeb40', 'AH-cd98c0', 
            'AH-cd6d00', 'AH-cd44c0', 'AH-cd4480', 'AH-cc02c0', 'AH-cac600', 'AH-cbc640', 'AH-cd42c0']
else:
    print 'Codigo de hotel no valido'
    exit()


f=open('/var/log/clientes/clientes.log')

hours=[]
clients = numpy.zeros((300, len(APList)))
t=0
time=''
APlocation={}

while True:
    c = f.readline().replace('\n','')
    if not c: break
    if c.startswith('Hora'): continue
    try:
        date,ap,ip,location,count = c.split(';')
    except:
        #print 'string no bien formado: %s' % c
        continue
        
    #print date,day
    if ap in APList and date[0:10]==day:
        if not ap in APlocation: APlocation[ap]=location
        if not time: 
            time=date[0:len(date)-3]
            #print time
            #print len(hours)
            hours.append(time)
            clients[t][APList.index(ap)]=count
        elif time==date[0:len(date)-3] or abs(int(time[len(time)-2:])-int(date[len(date)-5:len(date)-3]))<5:
            #print "time: %s date: %s diff= %d" % (time, date, abs(int(time[len(time)-2:])-int(date[len(date)-5:len(date)-3])))
            clients[t][APList.index(ap)]=count
        else:
            #print "time: %s date: %s diff= %d" % (time, date, abs(int(time[len(time)-2:])-int(date[len(date)-5:len(date)-3])))
            time=date[0:len(date)-3]
            #print time
            #print len(hours)
            t=t+1
            hours.append(time)
            clients[t][APList.index(ap)]=count
        
    

#print len(hours)


lista=''
for a in APList:
    #print APlocation[a].split('@')[0].replace(' ','_').replace('"','')
    try:
        lista=lista+' '+APlocation[a].split('@')[0].replace(' ','_').replace('"','')
    except:
        lista=lista+' '+a
        

#print "Fecha Hora "+' '.join(map(str,APList))
print "Fecha Hora "+lista
for i in range(len(hours)):
    print hours[i], ' '.join(map(str, clients[i,:])).replace('.0','')
    
    
'''for a in APList:
    try:
        print a, APlocation[a]    
    except:
        print a'''
        
