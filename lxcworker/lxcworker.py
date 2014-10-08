#!/usr/bin/env python
import pika
import sys
import lxc
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='10.0.0.103'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_lxc_workers',
                         type='topic')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

binding_keys = ['lxc.server.*','lxc.server']

for binding_key in binding_keys:
    channel.queue_bind(exchange='topic_lxc_workers',
                       queue=queue_name,
                       routing_key=binding_key)

print(' [*] Waiting for commands. To exit press CTRL+C')


def callbacklxc(ch, method, properties, body):
	commands = {
		"getrunningservers" : get_running_servers_command,
	}
	body = body.decode('utf-8')
	print(" [x] %r:%r" % (method.routing_key, body,))
	if body not in commands : 
		print("Never heard of command named %r" %(body))
	else:
		commands[body]()

def get_running_servers_command():
	for container_name in lxc.list_containers():
		container = lxc.Container(container_name)
		print("container name %r:" % (container.name))
		print("container state %r:" % (container.state))	
		print("container MAC %r:" % (container.get_config_item("lxc.network.0.hwaddr")))
		print("container IPv4 %r:" % (container.attach_wait(lxc.attach_run_command, ["ifconfig", "eth0"])))		



channel.basic_consume(callbacklxc,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()

