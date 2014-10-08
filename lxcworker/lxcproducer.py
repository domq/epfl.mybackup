#!/usr/bin/env python
import pika
import sys

def callbackresponse(ch, method, properties, body):
	body = body.decode('utf-8')
	print(body)
	connection.close()
	exit()

def callbacktimeout():
	print("Timeout")
	connection.close()
	exit()



connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='10.0.0.103'))
connection.add_timeout(30,callbacktimeout)
channel = connection.channel()

channel.exchange_declare(exchange='topic_lxc_workers',
                         type='topic')

channel.exchange_declare(exchange='topic_lxc_master',
                         type='topic')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

routing_key = sys.argv[1] if len(sys.argv) > 1 else 'anonymous.info'
message = sys.argv[2]
channel.basic_publish(exchange='topic_lxc_workers',
                      routing_key=routing_key,
                      body=message)
print ("[x] Sent %r:%r  -- waiting for reply" % (routing_key, message))

channel.queue_bind(exchange='topic_lxc_master',
                       queue=queue_name,
                       routing_key="lxc.master")

channel.basic_consume(callbackresponse,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()
connection.close()
