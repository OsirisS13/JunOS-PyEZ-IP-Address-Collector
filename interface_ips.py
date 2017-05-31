from jnpr.junos import Device
import jnpr.junos
#for user prompt to enter passwords 
from getpass import getpass
#used to parse the xml???
from lxml import etree
import sys
#from myTables.ConfigTables import InterfaceTable
from jnpr.junos.factory.factory_loader import FactoryLoader
import yaml

#this YAML data should be stored in a separate file and called properly (see https://github.com/Juniper/py-junos-eznc/tree/master/lib/jnpr/junos/op for examples how), but I'm lazy so just putting it here
# YAML data is used to access the different "tables" or "views" in Junos (which really are just the different sections)
#xpath used for the items and fields
#table is the rpc callable
#view is the fields you want within the rpc/table
yaml_data="""
---
InterfaceTable:
  rpc: get-interface-information
  args:
   interface_name: '[afgxe][et]-*' 
  item: physical-interface/logical-interface
  key: name
  view: InterfaceView
  
InterfaceView:
  fields:
    name: name
    description: ../description
    family: address-family/address-family-name
    interfaceaddress: address-family/interface-address/ifa-local
"""
#This is needed to load the YAML 
globals().update(FactoryLoader().load(yaml.load(yaml_data)))

#function to write data to text file
def writefile(name, hostname, ipaddress,interface,  description):
	#open file in append mode, will create if file doesnt exist
	file = open(name,'a')
	#write file
	file.write(hostname + ',' + interface + ',' + ipaddress + ',' + description + '\n' )
	print ('%s file written' %name)
	return

def get_data(ipaddress, username, passwd):
	#check to see if netconf is reachable, otherwise timeout after the value (in seconds)
	Device.auto_probe = 1
	#create device object
	dev = Device(host=ipaddress, user=username, password=passwd, port = "22" )
	#connet to device
	try:
		dev.open()
		print("\nNETCONF connection to %s opened!" %ipaddress)
		print("Beginning data collection...\n")
		#collect data
		#store facts
		devicefacts = dev.facts
		#get hostname
		hostname = devicefacts['hostname'].replace("'","")
		print hostname
		#get interface info using custom table defined above in YAML section
		interface = InterfaceTable(dev)
		interface.get(interface_name = "ae*")
		for interface in interface:
			if "ae" in interface.name and ".0" in interface.name:
				
				print 'name: ', interface.name
				print 'interface address: ', interface.interfaceaddress
				print 'description: ', interface.description
				writefile(hostname + " Interface IPs.csv",hostname, interface.interfaceaddress, interface.name,interface.description)
			elif "fxp0.0" in interface.name:
				print 'name: ', interface.name
				print 'interface address: ', interface.interfaceaddress
	
		print("\nOperation Complete.")
		dev.close()
		print("NETCONF connection to %s is now closed.\n" %ipaddress)
	#if probe times out and raises a probe error
	except jnpr.junos.exception.ProbeError as e: 
		print("NETCONF connection to %s is not reachable, moving on.." %ipaddress)
	#any other error
	except Exception as e:
		print (e)

#user inputs
user = raw_input("Username: ")	
passwd = getpass("Device password: ")
startip = input("Enter start third octect number: ")
endip = input("Enter end third octect number: ")
#generate and loop through data collection for ip addresses from 10.189.x.10 where x begins at intial "i" value and ends at the while < value.
i = startip
while i < endip:
        val = str(i)
        currentip = ( "10.189.%s.10" %val)
        i = i + 1
		#call actual data collection function
	get_data(currentip,user, passwd)
