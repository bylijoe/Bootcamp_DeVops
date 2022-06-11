#!/usr/bin/env python
import glob, os
import gzip
import argparse
from time import strptime, mktime
from datetime import timedelta, datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


__author__ = 'Julian Garcia-Sotoca Pascual'

parser = argparse.ArgumentParser(description='Script para el analisis de logs de dispositivos de red')
parser.add_argument('-f','--file', help='Fichero a analizar',required=False)
parser.add_argument('-r','--hotel',help='Hotel por el que se quiere filtrar', required=False)
parser.add_argument('-d','--day',help='Dia que se quiere analizar', type=int, required=False, default=1)
parser.add_argument('-a','--all',help='Analiza todos los logs. Se puede filtrar por hotel', required=False, action='store_true')
parser.add_argument('-v','--verbose',help='Lanza el script en modo verbose', required=False, action='store_true')
args = parser.parse_args()

offset=args.day
hotel=args.hotel
manualFile=args.file
alllogs=args.all

def sendmail(text, h, subject):
    me = 'loganalizer@hotels.com'
    you = 'juliansotoca@hotels.com'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = you
    html= '''\
    <html>
    <head></head>
    <body> <h3>%s</h3><hr>
    <p>Numero total de errores registrados: %d</p>
    <p>Numero total de puertos flapeando: %d</p><hr>
    %s
    </body>
    </html>
    ''' % (subject, len(errList), len(flappingIF), h)
    part2 = MIMEText(html, 'html')
    msg.attach(part2)
    s = smtplib.SMTP('relay.hotels.red')
    s.sendmail(me, you, msg.as_string())
    s.quit()


def registerError(m,h,d):   
    lastStatus=errList.get((h,m))
    if lastStatus:
        d_last=d
        errList[(h,m)]=[lastStatus[0]+1,lastStatus[1], d_last]
    else:
        d_ini=d
        d_last=d
        errList[(h,m)]=[1,d_ini, d_last]
    


def printErrors():
    print "ERROR SUMMARY"
    html='<h2>ERROR SUMMARY</h2><hr><table style="width:100%">'
    html=html+"<tr><td>Device:</td><td>Error:</td><td>Repetido:</td><td>Primero:</td><td>Ultimo:</td></tr>"
    print "#"*40
    for tup in sorted(errList):
        print "[WARNING] Device: %s - Error: %s" % (tup[0], tup[1])
        html=html+"<tr><td>%s</td><td>%s</td><td>%d</td><td>%s</td><td>%s</td></tr>" % (tup[0], tup[1], errList[tup][0], errList[tup][1], errList[tup][2])
    print "#"*40
    print "\nTotal errors: %d" % len(errList)
    print "#"*40
    html=html+'<tr><td>Total errors: %d</td></tr></table>' % len(errList)
    return html

def getHotelName(file):
    return file.replace('w-','').split('.')[0]

def getHotelList():
    os.chdir(LOGDIR)
    hotelList=[]
    for file in glob.glob('*.log*'):
        f=file.replace('w-','').split('.')[0]
        if not f in hotelList:
            hotelList.append(f)
    return hotelList
    
def getFileList(hotel):
    os.chdir(LOGDIR)
    fileList=[]
    files=glob.glob('*%s.log*' % hotel)
    files.sort(key=os.path.getmtime)
    for file in files:
        if not file in fileList:
            fileList.append(file)
    return fileList
    
def getHotelsLogFiles():
    os.chdir(LOGDIR)
    logList=[]
    for file in glob.glob('*.log'):
        f=file.replace('w-','').replace('.log','')
        if not f in logList:
            logList.append(f)
    return logList

def getLogFile(h):
    os.chdir(LOGDIR)
    logList=[]
    for f in glob.glob('*%s.log*' % h):
        if not f in logList:
            logList.append(f)
    return logList
    
def printOption(h):
    logList=getHotelsLogFiles()
    if not h in logList:
        print 'No se puede abrir el fichero %s. Opciones posibles:\n%s' % ((LOGDIR+LOGFILE), " ".join(logList))
    else:
        print 'No se puede abrir el fichero %s. Opciones posibles:\n%s' % ((LOGDIR+LOGFILE), " ".join(getLogFile(h)))

def analyzeDate(d,h):
    
    now = datetime.now()
    maxoffset=timedelta(days=offset+1)
    #print "fecha log: %s" % d
    if d.split()[3].isdigit():
        logdate=strptime(d, '%b %d %H:%M:%S %Y')
    else:
        y=now.year
        logdate=strptime('%s %d' % (d[0:15],y), '%b %d %H:%M:%S %Y')
    logdatedt=datetime.fromtimestamp(mktime(logdate))
    if ( now - logdatedt ) > maxoffset:
        warnmessage = 'Dispositivo %s con un desfase superior a %d dias' % (h,offset)
        registerError(warnmessage, h, d)

def flappingIncrement(m,h):
    if 'DOWN' in m:
        status='DOWN'
    else:
        status='UP'
    if args.verbose:
        print m.split()
    iface='UNKNOWN'
    for i in m.split():
        if 'Ethernet' in i:
            iface=i
        elif 'Bridge-Aggregation' in i:
            iface=i
        elif 'port' in i:
            pindex=m.find('port')
            iface='Port %s' % m[pindex+5]
        elif 'Port' in i:
            pindex=m.find('Port')
            iface='Port %s' % m[pindex+5]
    lastStatus=flappingIF.get((h,iface))
    if lastStatus:
        flappingIF[(h,iface)]=[lastStatus[0]+1,status]
    else:
        flappingIF[(h,iface)]=[1,status]
    
def printFlappings():
    print "\n\nFLAPPING SUMMARY"
    html='<br><h2>FLAPPING SUMMARY</h2><hr><table style="width:100%">'
    html=html+"<tr><td>Dispositivo</td><td>Interfaz</td><td>Flapeos</td><td>Ultimo estado</td></tr>"
    print "#"*40
    if args.verbose:
        print flappingIF
    for f in sorted(flappingIF):
        print "Device %s - Interface: %s: flapped %d times. Last status %s" % (f[0], f[1], flappingIF[f][0], flappingIF[f][1])
        html=html+"<tr><td>%s</td><td>%s</td><td>%d</td><td>%s</td></tr>" % (f[0], f[1], flappingIF[f][0], flappingIF[f][1])
    print "#"*40
    html=html+'</table>'
    return html

def analyze(files):
    if args.verbose:
        print " ".join(files)
    for LOGFILE in files:
        if LOGFILE.find('gz') >0:      
            try:
                f = gzip.open(LOGDIR+LOGFILE, 'rb')
            except:
                printOption(hotel)
                exit(1)
        else:
            try:
                f = open(LOGDIR+LOGFILE, 'r')
            except:
                printOption(hotel)
                exit(1)
        if len(LOGFILE.split('.'))>2:
            offset=int(LOGFILE.split('.')[2])
        for line in f:
            date=line[0:20]
            line=line.replace('\n','')
            l=line.split()
            if l[3].isdigit():
                hostname=l[4]
            else:
                hostname=l[3]
            messageOffset=line.find(hostname)+len(hostname)+1
            if hostname=='INFO':
                hostname='3COM-%s' % getHotelName(LOGFILE)
            try:
                modulo,message=line[messageOffset:len(line)].split(':',1)
            except:
                message=line[messageOffset:len(line)]
            if any(x in message for x in ignoredMessages):
                continue
            else:
                #print message
                if any(x in message for x in ('UP', 'up', 'Up', 'down', 'DOWN', 'Down')):
                    flappingIncrement(message,hostname)
                else:
                    registerError(message, hostname, date)
                analyzeDate(date, hostname)

    
#VARIABLES GLOBALES    
LOGDIR='/var/log/network/'
ignoredMessages=['current power', 
                'SSH', 
                'Trap', 
                'System clock changed', 
                'local-Service=login-UserName=admin@system',
                'forwarding state',
                'User=admin; Command is',
                'System stratum changed',
                'STP status Forwarding',
                'command information',
                'Exit from configuration mode',
                'admin logged out from',
                '[USER_INFO_OFFLINE]',
                'Last message repeated',
                'state as forwarding',
                'user:admin command',
                ' 1.3.6.1.4.']


filesToAnalyze=[]
if alllogs:
    if hotel:
        filesToAnalyze=getFileList(hotel)
        mailSubject='Analisis de todos los ficheros del hotel %s' % hotel
    else:
        filesToAnalyze=getFileList('')
        mailSubject='Analisis de todos los ficheros de log disponibles en %s' % LOGDIR
    
else:
    if manualFile:
        LOGFILE=manualFile
        if args.day: print 'Warning: Si se especifica la opcion --file la opcion --day es ignorada'
        if len(LOGFILE.split('.'))>2:
            offset=int(LOGFILE.split('.')[2])
    elif hotel:
        if offset>1:
            LOGFILE='%s.log.%d.gz' % (hotel,offset)
        elif offset == 1:
            LOGFILE='%s.log.%d' % (hotel,offset)
        else:
            LOGFILE='%s.log' % hotel
    else:
        #print "No se ha especificado ni hotel ni fichero a analizar"
        parser.error("No se ha especificado ni hotel ni fichero a analizar. --file or --hotel required.")
        exit(1)
    mailSubject='Analisis del fichero %s' % LOGFILE
    filesToAnalyze.append(LOGFILE)    
    
             
errList={}
flappingIF={}


analyze(filesToAnalyze) 

html1=printErrors()
html2=printFlappings()
sendmail('Resumen errores', html1+html2, mailSubject)
