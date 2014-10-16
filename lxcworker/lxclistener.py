#!/usr/bin/env python
import pika
import sys
import json

timeout=30


def callbackresponse(ch, method, properties, body):
	body = body.decode('utf-8')
	print(json.dumps(json.loads(body),sort_keys=True,indent=4, separators=(',', ': ')))

def callbacktimeout():
	print("Timeout")
	connection.close()
	exit()



connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='10.0.0.103'))
# connection.add_timeout(timeout,callbacktimeout)
channel = connection.channel()

# create the topic on the rabbitmq server, if not already done
channel.exchange_declare(exchange='lxc',type='topic',durable=True,auto_delete=True)

#declare the queue on the rabbitmq server, if not already done
result = channel.queue_declare(durable=False, exclusive=False, auto_delete=True)
queue_name = result.method.queue

#wait the reply for [timeout] seconds
channel.queue_bind(exchange='lxc',
                       queue=queue_name,
                       routing_key="lxc.master")

channel.basic_consume(callbackresponse,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()
connection.close()
