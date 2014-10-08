#!/usr/bin/env python
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
						"\taddRedirect [port sourceIP destinationIP]\n"+
						"\taddRedirectToContainer [port sourceIP containerName]\n"+
						"\tdeleteRulesForSourceIP [ip]\n"+
						"\tdeleteRulesForDestIP [ip]\n"+
						"\tcloneAndStartContainer [source_name new_name]\n"+
						"\tgetContainerIP [container_name]\n"+
						"\tprintContainersAsJSON\n"+
						"\taddUserToContainer [username container_name]\n"+
						"\tdeleteRedirectToContainer [containerName]")
	exit()
else:
	if sys.argv[1]=="listRulesOnPort":
		if len(sys.argv)!=3:
			print("specify a port : listRulesOnDPort [port]")
			exit()
		else:
			lxcproc.printIptablesRulesOnDPort(sys.argv[2])

	elif sys.argv[1]=="deleteRulesOnPort":
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
		if len(sys.argv)!=5:
			print("specify a port, source IP and destination IP : addRedirect [port sourceIP destinationIP]")
			exit()
		else:
			lxcproc.addRedirectOfDPort(sys.argv[2], sys.argv[3], sys.argv[4])

	elif sys.argv[1]=="getContainerIP":
		if len(sys.argv)!=3:
                        print("specify a container name : getContainerIP [containerName]")
                        exit()
		else:
			print(lxcproc.getContainerIP(sys.argv[2]))

	elif sys.argv[1]=="addRedirectToContainer":
		if len(sys.argv)!=5:
			print("specify a port, source IP and container name : addRedirectToContainer [port sourceIP containerName]")
			exit()
		else:
			lxcproc.addRedirectOfDPortToContainer(sys.argv[2], sys.argv[3], sys.argv[4])

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
			print("specify a username andcontainer name : addUserToContainer [username container_name]")
			exit()
		else:
			lxcproc.addUserToContainer(sys.argv[2], sys.argv[3])
			exit()

	elif sys.argv[1]=="printContainersAsJSON":
		print(lxcproc.getContainersAsJSON())
		exit()


	else:
		print("unknown command: "+sys.argv[1])






