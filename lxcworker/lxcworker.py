#!/usr/bin/env python3
import pika
import sys
import lxc
import json
import socket
import lxcproc
import threading

#lxcworker.py

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='10.0.0.103'))
channel = connection.channel()

channel.exchange_declare(exchange='lxc',type='topic',durable=True,auto_delete=True)

result = channel.queue_declare(durable=False, exclusive=False, auto_delete=True)
queue_name = result.method.queue


binding_keys = ['lxc.server.*','lxc.server', 'lxc.server.'+socket.gethostname(), 'lxc.server.'+socket.gethostbyname(socket.gethostname())]

for binding_key in binding_keys:
    channel.queue_bind(exchange='lxc',
                       queue=queue_name,
                       routing_key=binding_key)

print(' [*] Waiting for commands. To exit press CTRL+C')

def reply(command):
	channel.basic_publish(exchange='lxc',
                      routing_key="lxc.master",
                      body=lxcproc.jsonify(command()))

def sendState():
	channel.basic_publish(exchange='lxc',
                      routing_key="lxc.master",
                      body=lxcproc.jsonify(lxcproc.getContainers()))
	threading.Timer(5, sendState).start()


def callbacklxc(ch, method, properties, body):
	commands = {
		"getcontainers" : lxcproc.getContainers,
	}
	body = body.decode('utf-8')
	print(" [x] %r:%r" % (method.routing_key, body,))
	if body not in commands : 
		print("Never heard of command named %r" %(body))
	else:
		reply(commands[body])





channel.basic_consume(callbacklxc,
                      queue=queue_name,
                      no_ack=True)

sendState()

channel.start_consuming()


