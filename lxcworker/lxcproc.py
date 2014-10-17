#!/usr/bin/env python
import pika
import sys
import lxc
import json
import iptc
import socket
import augeas

table=iptc.Table(iptc.Table.NAT)
chain=iptc.Chain(table, "PREROUTING")
HOSTNAME=socket.gethostname()
CONTAINER_PATH = "/var/lib/lxc/"
MYROOT="/"


def getContainer(container_name):
	container = lxc.Container(container_name)
	if container.defined :
		result={}
		result["class"]="ch.epfl.mybackup.beans.Container"  #for java deserialization
		result["name"]=container_name
		result["state"]=container.state
		if container.state!="STOPPED":
			result["MAC"]=container.network[0].hwaddr
			result["IPv4"]=container.get_ips(interface="eth0", timeout=30)[0]
			ipforwards=getDestIPForward(result["IPv4"])
			if ipforwards :
				result["IpForwards"]=ipforwards
		return result
	else:
		print("the container is not defined!")

def getContainers():
	result=[]
	for container_name in lxc.list_containers():
		result.append(getContainer(container_name))
	finalresult={"class":"ch.epfl.mybackup.beans.Server","hostname":HOSTNAME,"hostIP":socket.gethostbyname(socket.gethostname()),"containers":result}
	return finalresult

def getContainerIP(container_name):
	if existsContainer(container_name):
		container=lxc.Container(container_name)
		if container.running:
			ipaddress=container.get_ips(interface="eth0", timeout=0.5)
			return ipaddress[0]
		else:
			print("the container is stopped")
	else:			
		print("no container named "+container_name+" found!")

def existsContainer(container_name):
	container=lxc.Container(container_name)
	return container.defined

		
	

def cloneAndStartContainer(source_name, new_name):
	if not existsContainer(source_name):
		print("container "+source_name+" doesn't exist !")
	elif existsContainer(new_name):
		print("container "+new_name+" exists already !")
	elif lxc.Container(source_name).running:
		print("the container "+source_name+" is running, stop it first (lxc-stop -n"+source_name+")")
	else:
		container_source=lxc.Container(source_name)
		container_destination=container_source.clone(new_name)
		container_destination.start()
		ipadresses=container_destination.get_ips(timeout=60)
		print("the container "+new_name+" was started with IP "+ipadresses[0])


def matchIptablesRulesOnDPort(dport):
	table.refresh()
	rules=[]
	for rule in chain.rules:
		for match in rule.matches:
			if match.dport==str(dport):
				rules.append(rule)
	return rules
	
def getDestIPForward(dest_ip):
	rules=matchIptablesRulesOnDestIp(dest_ip)
	results=[]
	for rule in rules:
		result={}
		result["class"]="ch.epfl.mybackup.beans.IpForward" # java deserialization
		result["dest"]=dest_ip
		result["port"]=rule.matches[0].dport
		result["source"]=rule.dst.split("/", 1 )[0];
		result["protocol"]=rule.protocol
		results.append(result)
	return results
	


def printRule(rule):
	for match in rule.matches:
		print(rule.target.name+" from: "+rule.dst+":"+match.dport+" redirect to "+rule.target.to_destination)


def printIptablesRulesOnDPort(dport):
	for rule in matchIptablesRulesOnDPort(dport):
		printRule(rule)


def deleteIptablesRulesOnDPort(dport):
	rules=matchIptablesRulesOnDPort(dport)
	table.autocommit = False
	for rule in rules:
		print("deleting :")
		printRule(rule)
		chain.delete_rule(rule)
	table.commit()
	table.autocommit = True

def matchIptablesRulesOnSourceIP(sourceIP):
	table.refresh()
	rules=[]
	for rule in chain.rules:
		if rule.dst.startswith(sourceIP):
			rules.append(rule)
	return rules

def matchIptablesRulesOnDestIp(destIP):
	table.refresh()
	rules=[]
	for rule in chain.rules:
		if rule.target.to_destination.startswith(destIP):
			rules.append(rule)
	return rules

def deleteIptablesRulesForSourceIP(ip):
	rules=matchIptablesRulesOnSourceIP(ip)	
	table.autocommit = False
	for rule in rules:
		print("deleting: ")
		printRule(rule)
		chain.delete_rule(rule)
	table.commit()
	table.autocommit = True

def deleteIptablesRulesForDestIP(ip):
	rules=matchIptablesRulesOnDestIp(ip)
	table.autocommit = False
	for rule in rules:
		print("deleting: ")
		printRule(rule)
		chain.delete_rule(rule)
	table.commit()
	table.autocommit = True

def deleteIptablesRulesForContainer(container_name):
	container_ip=getContainerIP(container_name)
	deleteIptablesRulesForDestIP(container_ip)
	

	
def addRedirectOfDPort(port,sourceIP,destinationIP,protocol):
	if not existsRedirectForIpPortAndProtocol(port,sourceIP,protocol):
		rule = iptc.Rule()
		rule.dst=sourceIP
		rule.protocol=protocol
		target=rule.create_target("DNAT")
		target.to_destination=destinationIP+":"+port
		match = rule.create_match(protocol)
		match.dport=port
		chain.insert_rule(rule)
	else:
		print("the "+protocol+" rule for "+sourceIP+":"+port+" exists already!")

def existsRedirectForIpPortAndProtocol(port,sourceIP,protocol):
	rules=matchIptablesRulesOnDPort(port)
	for rule in rules:
		if rule.dst==sourceIP+"/255.255.255.255" and rule.protocol==protocol:
			return True
	return False

def addRedirectOfDPortToContainer(port,sourceIP,containerName, protocol):
	container_ip=getContainerIP(containerName)
	addRedirectOfDPort(port,sourceIP,container_ip,protocol)

def addUserToContainer(username, container_name):
	container=lxc.Container(container_name)
	if container.running :
		result=container.attach_wait(lxc.attach_run_command, ["/sbin/adduser", username])
		if(result!=0) : 
			print("user exists already!")
			return result
		else : return result
	else : 
		print("container "+container_name+" is not running!")
		return result

def getUsersInContainer(container_name):
	container=lxc.Container(container_name)
	if not container.defined : return (False,"The container "+container_name+" doesn't exist")
	etcpasswd=open(CONTAINER_PATH+container_name+"/rootfs/etc/passwd","r")
	usernames=[]
	for line in etcpasswd.readlines():
		username={}
		splittedline=line.split(":")
		username["username"]=splittedline[0]
		username["pid"]=splittedline[2]
		username["gid"]=splittedline[3]
		username["description"]=splittedline[4]
		username["home"]=splittedline[5]
		username["shell"]=splittedline[6].rstrip('\n')
		usernames.append(username)
	return usernames

def prettyjsonify(structure):
	return json.dumps(structure,sort_keys=True,indent=4, separators=(',', ': '))

def jsonify(structure):
	return json.dumps(structure)


def getRealUsersInContainer(container_name):
	users=getUsersInContainer(container_name)
	resultusers=[]
	for user in users:
		if user["home"].startswith("/home/"):
			resultusers.append(user)
	return resultusers

def getDNS():
	a = augeas.Augeas(root=MYROOT) 
	matches = a.match("/files/etc/hosts/*/*")
	for match in matches:
		print(a.get(match))

	







