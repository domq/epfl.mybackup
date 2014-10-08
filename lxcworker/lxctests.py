#!/usr/bin/env python
import pika
import sys
import lxc
import json
import iptc

table=iptc.Table(iptc.Table.NAT)
chain=iptc.Chain(table, "PREROUTING")

def get_running_servers_command():
	for container_name in lxc.list_containers():
		container = lxc.Container(container_name)
		print("container name %r:" % (container.name))
		print("container state %r:" % (container.state))	
		print("container MAC %r:" % (container.get_config_item("lxc.network.0.hwaddr")))
		print("container IPv4 %r:" % (container.get_ips(interface="eth0", timeout=0.5)))		

def getContainerIP(container_name):
	if existsContainer(container_name):
		container=lxc.Container(container_name)
		if (container.state != "STOPPED"):
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
	return (container.state == "STOPPED")

		
	

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




if len(sys.argv) <2 :
	print ("please specify a command from :\n\tlistRulesOnDPort [port]\n"+
						"\tdeleteRulesOnDPort [port]\n"+
						"\taddRedirect [port sourceIP destinationIP]\n"+
						"\taddRedirectToContainer [port sourceIP containerName]\n"+
						"\tdeleteRulesForSourceIP [ip]\n"+
						"\tdeleteRulesForDestIP [ip]\n"+
						"\tcloneAndStartContainer [source_name new_name]\n"+
						"\tgetContainerIP [container_name]\n"+
						"\tdeleteRedirectToContainer [containerName]")
	exit()
else:
	if sys.argv[1]=="listRulesOnPort":
		if len(sys.argv)!=3:
			print("specify a port : listRulesOnDPort [port]")
			exit()
		else:
			printIptablesRulesOnDPort(sys.argv[2])

	elif sys.argv[1]=="deleteRulesOnPort":
		if len(sys.argv)!=3:
			print("specify a port : deleteRulesOnDPort [port]")
			exit()
		else:
			deleteIptablesRulesOnDPort(sys.argv[2])

	elif sys.argv[1]=="deleteRulesForSourceIP":
		if len(sys.argv)!=3:
			print("specify an IP : deleteRulesForSourceIP [ip]")
			exit()
		else:
			deleteIptablesRulesForSourceIP(sys.argv[2])

	elif sys.argv[1]=="deleteRulesForDestIP":
		if len(sys.argv)!=3:
			print("specify an IP : deleteRulesForDestIP [ip]")
			exit()
		else:
			deleteIptablesRulesForDestIP(sys.argv[2])

	elif sys.argv[1]=="addRedirect":
		if len(sys.argv)!=5:
			print("specify a port, source IP and destination IP : addRedirect [port sourceIP destinationIP]")
			exit()
		else:
			addRedirectOfDPort(sys.argv[2], sys.argv[3], sys.argv[4])

	elif sys.argv[1]=="getContainerIP":
		if len(sys.argv)!=3:
                        print("specify a container name : getContainerIP [containerName]")
                        exit()
		else:
			print(getContainerIP(sys.argv[2]))

	elif sys.argv[1]=="addRedirectToContainer":
		if len(sys.argv)!=5:
			print("specify a port, source IP and container name : addRedirectToContainer [port sourceIP containerName]")
			exit()
		else:
			addRedirectOfDPortToContainer(sys.argv[2], sys.argv[3], sys.argv[4])

	elif sys.argv[1]=="deleteRedirectToContainer":
		if len(sys.argv)!=3:
			print("specify a container name : deleteRedirectToContainer [containerName]")
			exit()
		else:
			deleteIptablesRulesForContainer(sys.argv[2])
			exit()

	elif sys.argv[1]=="cloneAndStartContainer":
		if len(sys.argv)!=4:
			print("specify a source and new container name : cloneAndStartContainer [source_name new_name]")
			exit()
		else:
			cloneAndStartContainer(sys.argv[2], sys.argv[3])
			exit()

	else:
		print("unknown command: "+sys.argv[1])






