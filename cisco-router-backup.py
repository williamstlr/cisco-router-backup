#!/usr/bin/python
#You need to successfully ssh into the device manusally to accept the hostkey once  for this to work.
import pexpect
import sys
import re
import time
import os.path
import syslog
from subprocess import call
import os
import argparse


#setup argument parser
parser = argparse.ArgumentParser()
parser.add_argument("device", help="Hostname or IP Address of device to be backed up")
parser.parse_args()
args = parser.parse_args()


credentialsFile="./cred-file"
ftp_backup_location = "/home/netbackup/cisco/"
date_time = time.strftime("%m.%d.%Y_%H:%M")
syslog.syslog('Starting ' + parser.prog)

#Read credentials in
with open(credentialsFile) as f:
        credentials=f.readlines()


#set a bunch of names
router_user=credentials[0].rstrip()
router_pass=credentials[1].rstrip()
router = args.device
backup_file_name = router + "_" + date_time + ".cfg"
backup_full_path = ftp_backup_location+router + "/" + backup_file_name

#If the backup location dosen't exist for this device, create it and chown it
if os.path.isdir(ftp_backup_location+router) == False:
        syslog.syslog("Backup folder doesn't exist, creating it")
        call(["mkdir", "-p",ftp_backup_location+router])
        call(["chown","netbackup:netbackup",ftp_backup_location+router])



#Attempt to connect to the router
syslog.syslog("Attempting to login to " + router)
try:
        child = pexpect.spawn('ssh %s@%s -1' % (router_user, router))
#       child.logfile = sys.stdout #uncomment to enable debugging
        child.timeout = 5
        child.expect('password:')

except pexpect.TIMEOUT:
        syslog.syslog("Did not receive login prompt. Exiting")
        exit(1)


#Login to router
child.sendline(router_pass)
child.expect('>')
syslog.syslog("Router login successful")

#Run backup
syslog.syslog("Starting FTP backup")
child.sendline('copy run ftp')
child.expect("\?")
child.sendline('hcusyslog')
child.expect('\?')
child.sendline(backup_full_path)

#Log out of router
syslog.syslog("Logging out of the router")
child.sendline('exit')
child.expect('>')
child.sendline('exit')

#Verify that the created backup file now exists
if os.stat(ftp_backup_location+router+"/"+backup_file_name) > 0:
        print("Backup was successful")
        syslog.syslog("Backup was successful. Located at " + ftp_backup_location+router+"/"+backup_file_name)


else:
        print("Backup file was less that 0 byes. The backup probably failed")
        syslog.syslog("Backup file was less that 0 byes. The backup probably failed")

#Exit
exit (0)
