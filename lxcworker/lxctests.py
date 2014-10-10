#!/usr/bin/env python3
import pika
import sys
import lxc
import json
import iptc
import lxcproc

table=iptc.Table(iptc.Table.NAT)
chain=iptc.Chain(table, "PREROUTING")




if len(sys.argv) <2 :
	print ("please specify a command from :\n\tlistRulesOnDPort [port]\n"+
						"\tdeleteRulesOnDPort [port]\n"+
						"\taddRedirect [port sourceIP destinationIP protocol]\n"+
						"\taddRedirectToContainer [port sourceIP containerName protocol]\n"+
						"\tdeleteRulesForSourceIP [ip]\n"+
						"\tdeleteRulesForDestIP [ip]\n"+
						"\tcloneAndStartContainer [source_name new_name]\n"+
						"\tgetContainerIP [container_name]\n"+
						"\tprintContainers\n"+
						"\taddUserToContainer [username container_name]\n"+
						"\tlistRealUsersInContainer [container_name]\n"+
						"\tdeleteRedirectToContainer [containerName]")
	exit()
else:
	if sys.argv[1]=="listRulesOnDPort":
		if len(sys.argv)!=3:
			print("specify a port : listRulesOnDPort [port]")
			exit()
		else:
			lxcproc.printIptablesRulesOnDPort(sys.argv[2])

	elif sys.argv[1]=="deleteRulesOnDPort":
		if len(sys.argv)!=3:
			print("specify a port : deleteRulesOnDPort [port]")
			exit()
		else:
			lxcproc.deleteIptablesRulesOnDPort(sys.argv[2])

	elif sys.argv[1]=="deleteRulesForSourceIP":
		if len(sys.argv)!=3:
			print("specify an IP : deleteRulesForSourceIP [ip]")
			exit()
		else:
			lxcproc.deleteIptablesRulesForSourceIP(sys.argv[2])

	elif sys.argv[1]=="deleteRulesForDestIP":
		if len(sys.argv)!=3:
			print("specify an IP : deleteRulesForDestIP [ip]")
			exit()
		else:
			lxcproc.deleteIptablesRulesForDestIP(sys.argv[2])

	elif sys.argv[1]=="addRedirect":
		if len(sys.argv)!=6:
			print("specify a port, source IP, destination IP and protocol (tcp|udp): addRedirect [port sourceIP destinationIPi protocol]")
			exit()
		else:
			lxcproc.addRedirectOfDPort(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

	elif sys.argv[1]=="getContainerIP":
		if len(sys.argv)!=3:
                        print("specify a container name : getContainerIP [containerName]")
                        exit()
		else:
			print(lxcproc.getContainerIP(sys.argv[2]))

	elif sys.argv[1]=="addRedirectToContainer":
		if len(sys.argv)!=6:
			print("specify a port, source IP, container name and the protocol (tcp|udp): addRedirectToContainer [port sourceIP containerName protocol]")
			exit()
		else:
			lxcproc.addRedirectOfDPortToContainer(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

	elif sys.argv[1]=="deleteRedirectToContainer":
		if len(sys.argv)!=3:
			print("specify a container name : deleteRedirectToContainer [containerName]")
			exit()
		else:
			lxcproc.deleteIptablesRulesForContainer(sys.argv[2])
			exit()

	elif sys.argv[1]=="cloneAndStartContainer":
		if len(sys.argv)!=4:
			print("specify a source and new container name : cloneAndStartContainer [source_name new_name]")
			exit()
		else:
			lxcproc.cloneAndStartContainer(sys.argv[2], sys.argv[3])
			exit()
	elif sys.argv[1]=="addUserToContainer":
		if len(sys.argv)!=4:
			print("specify a username and container name : addUserToContainer [username container_name]")
			exit()
		else:
			lxcproc.addUserToContainer(sys.argv[2], sys.argv[3])
			exit()
	elif sys.argv[1]=="listRealUsersInContainer":
		if len(sys.argv)!=3:
			print("specify a container name : listRealUsersInContainer [container_name]")
			exit()
		else:
			print(lxcproc.prettyjsonify(lxcproc.getRealUsersInContainer(sys.argv[2])))
			exit()


	elif sys.argv[1]=="printContainers":
		print(lxcproc.prettyjsonify(lxcproc.getContainers()))
		exit()


	else:
		print("unknown command: "+sys.argv[1])






