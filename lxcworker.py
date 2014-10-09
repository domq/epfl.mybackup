#!/usr/bin/env python
import pika
import sys
import lxc
import json
import lxcproc

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
		"getservers" : lxcproc.getContainersAsJSON,
	}
	body = body.decode('utf-8')
	print(" [x] %r:%r" % (method.routing_key, body,))
	if body not in commands : 
		print("Never heard of command named %r" %(body))
	else:
		commands[body]()


channel.basic_consume(callbacklxc,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()

