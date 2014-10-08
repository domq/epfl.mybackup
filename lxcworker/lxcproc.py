#!/usr/bin/env python
import pika
import sys
import lxc
import json
import iptc
import socket

table=iptc.Table(iptc.Table.NAT)
chain=iptc.Chain(table, "PREROUTING")
hostname=socket.gethostname()

def getContainerAsDict(container_name):
	result={}
	container = lxc.Container(container_name)
	if container.defined :
		result[container_name]={}
		result[container_name]["name"]=container_name
		result[container_name]["state"]=container.state
		if container.state!="STOPPED":
			result[container_name]["MAC"]=container.network[0].hwaddr
			result[container_name]["IPv4"]=container.get_ips(interface="eth0", timeout=30)[0]
			ipforwards=getDestIPForwardAsDict(result[container_name]["IPv4"])
			if ipforwards :
				result[container_name]["IpForwards"]=getDestIPForwardAsDict(result[container_name]["IPv4"])
		return result
	else:
		print("the container is not defined!")
		exit()

def getContainersAsJSON():
	result=[]
	for container_name in lxc.list_containers():
		result.append(getContainerAsDict(container_name))
	finalresult={"hostname":hostname,"hostIP":socket.gethostbyname(socket.gethostname()),"containers":result}
	return json.dumps(finalresult)

def getContainerIP(container_name):
	if existsContainer(container_name):
		container=lxc.Container(container_name)
		if not container.stopped:
			ipaddress=container.get_ips(interface="eth0", timeout=0.5)
			return ipaddress[0]
		else:
			print("the container is stopped")
			exit()
	else:			
		print("no container named "+container_name+" found!")

def existsContainer(container_name):
	container=lxc.Container(container_name)
	return container.defined

def isStoppedContainer(source_name):
	container=lxc.Container(source_name)
	return container.stopped

		
	

def cloneAndStartContainer(source_name, new_name):
	if not existsContainer(source_name):
		print("container "+source_name+" doesn't exist !")
		exit()
	elif existsContainer(new_name):
		print("container "+new_name+" exists already !")
		exit()
	elif not isStoppedContainer(source_name):
		print("the container "+source_name+" is running, stop it first (lxc-stop -n"+source_name+")")
		exit()
	else:
		container_source=lxc.Container(source_name)
		container_destination=container_source.clone(new_name)
		container_destination.start()
		ipadresses=container_destination.get_ips(timeout=60)
		print("the container "+new_name+" was started with IP "+ipadresses[0])


def matchIptablesRulesOnDPort(dport):
	rules=[]
	for rule in chain.rules:
		for match in rule.matches:
			if match.dport==str(dport):
				rules.append(rule)
	return rules
	
def getDestIPForwardAsDict(dest_ip):
	rules=matchIptablesRulesOnDestIp(dest_ip)
	results=[]
	for rule in rules:
		result={}
		result["dest"]=dest_ip
		result["port"]=rule.matches[0].dport
		result["source"]=rule.dst
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
	rules=[]
	for rule in chain.rules:
		if rule.dst.startswith(sourceIP):
			rules.append(rule)
	return rules

def matchIptablesRulesOnDestIp(destIP):
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
	

	
def addRedirectOfDPort(port,sourceIP,destinationIP):
	if not existsRedirectForIpAndPort(port,sourceIP):
		rule = iptc.Rule()
		rule.dst=sourceIP
		rule.protocol="tcp"
		target=rule.create_target("DNAT")
		target.to_destination=destinationIP+":"+port
		match = rule.create_match("tcp")
		match.dport=port
		chain.insert_rule(rule)
	else:
		print("the rule for "+sourceIP+":"+port+" exists already!")
		exit()

def existsRedirectForIpAndPort(port,sourceIP):
	rules=matchIptablesRulesOnDPort(port)
	for rule in rules:
		if rule.dst==sourceIP+"/255.255.255.255":
			return True
	return False

def addRedirectOfDPortToContainer(port,sourceIP,containerName):
	container_ip=getContainerIP(containerName)
	addRedirectOfDPort(port,sourceIP,container_ip)

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
