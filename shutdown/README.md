#Shutdown

Script to automate shutdown of a lab environment
containing CloudBridge/NetScaler/SDX devices.
It is an exercise in Paramiko and Nitro and RESTful
API exposed on these appliances.

Expects a csv list available in the same directory 
as the script called devices.csv, which contains:
ip_address,name-label(any name),params

where params are : 

device-type = netscaler or cloudbridge or sdx
username (for login)
password (for login)

Format (in the case of an sdx):

ip_address,name-label,sdx:nsroot:nsroot

script requires (in addition to stdlib) :
Paramiko
NetScaler Nitro SDK for Python

