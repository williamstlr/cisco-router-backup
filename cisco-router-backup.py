#!/usr/bin/python
import pexpect
import sys
import re
import time
import os.path


credentialsFile="./cred-file"

#check to make sure we have a config file specified
if len(sys.argv) < 2 :
        print('USAGE: %s router-address' % (scriptName))
        print('EXAMPLE: %s 192.168.1.216' % (scriptName))
        exit(1)

if os.path.isfile(credentialsFile) == False:
        print("Credentials file not found")
        exit(1)



#Read credentials in
with open(credentialsFile) as f:
        credentials=f.readlines()


router_user=credentials[0].rstrip()
router_pass=credentials[1].rstrip()
router = sys.argv[1].rstrip()


#Attempt to connect to the router
try:
        child = pexpect.spawn('ssh %s@%s -1' % (router_user, router))
        child.logfile = sys.stdout
        child.timeout = 5
        child.expect('password:')

except pexpect.TIMEOUT:
        print ("Did not recieve login prompt")
        exit(1)


#Login to router
child.sendline(router_pass)
child.expect('>')
child.sendline('en')
child.expect('Password:')
child.sendline(router_pass)
child.expect('#')
#child.sendline('conf t')
#child.expect('#')

#Run backup
child.sendline('copy run ftp')
child.expect("\?")
child.sendline('hcusyslog')
child.expect('\?')
child.sendline(router+"-"+time.strftime("%d.%m.%Y")+".cfg")




#Log out of router
child.sendline('exit')
child.expect('#')
child.sendline('exit')


#Exit
print ("Program exited successfully, this did not mean the backup was successful")
exit (0)
