#!/usr/bin/env python
import pika
import sys
import json

timeout=30


def callbackresponse(ch, method, properties, body):
	body = body.decode('utf-8')
	print(json.dumps(json.loads(body),sort_keys=True,indent=4, separators=(',', ': ')))
	connection.close()
	exit()

def callbacktimeout():
	print("Timeout")
	connection.close()
	exit()



connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='10.0.0.103'))
connection.add_timeout(timeout,callbacktimeout)
channel = connection.channel()

# create the topic on the rabbitmq server, if not already done
channel.exchange_declare(exchange='lxc',
                         type='topic')

#declare the queue on the rabbitmq server, if not already done
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

routing_key = sys.argv[1] if len(sys.argv) > 1 else 'anonymous.info'
message = sys.argv[2]

# send to the routing key from the commandline the message from the commandline
channel.basic_publish(exchange='lxc',
                      routing_key=routing_key,
                      body=message)
print ("[x] Sent %r:%r  -- waiting for reply" % (routing_key, message))


#wait the reply for [timeout] seconds
channel.queue_bind(exchange='lxc',
                       queue=queue_name,
                       routing_key="lxc.master")

channel.basic_consume(callbackresponse,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()
connection.close()
