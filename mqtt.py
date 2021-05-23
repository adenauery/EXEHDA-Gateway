import json
import time
from json import dumps
from umqtt.simple import MQTTClient

from wdt import Watchdog
from utils import get_configs, log, get_date


class Subscribe:
	def __init__(self, subscribe_stack):
		configs = get_configs()

		self.ip = configs['broker_mqtt']['ip']
		self.port = configs['broker_mqtt']['port']
		self.user = configs['broker_mqtt']['user']
		self.password = configs['broker_mqtt']['pass']
		self.topic = bytes("GW_{}".format(configs['gateway']['uuid']), "utf-8")
		self.uuid = configs['gateway']['uuid']

		self.subscribe_stack = subscribe_stack

	def callback(self, _, msg):
		receive = str(bytes(msg), "utf-8")
		self.subscribe_stack.insert(receive)

	def connect(self):
		fail_notified = False
		while True:
			try:
				c = MQTTClient(self.uuid, self.ip, self.port, self.user, self.password, keepalive=120)
				c.set_callback(self.callback)
				c.connect()
				c.subscribe(self.topic)
				try:
					while True:
						fail_notified = False
						if True:
							c.wait_msg()
						else:
							c.check_msg()
							time.sleep(1)
				except Exception as e:
					if not fail_notified:
						fail_notified = True
						log("Subscribe: {}".format(e))
						c.disconnect()
			except Exception as e:
				if not fail_notified:
					fail_notified = True
					log("Subscribe-connection: {}".format(e))
			time.sleep(5)

class Publish:
	def __init__(self, publish_stack):
		configs = get_configs()

		self.ip = configs['broker_mqtt']['ip']
		self.port = configs['broker_mqtt']['port']
		self.user = configs['broker_mqtt']['user']
		self.password = configs['broker_mqtt']['pass']
		self.topic = bytes(configs['broker_mqtt']['topic'], "utf-8")
		self.uuid = configs['gateway']['uuid']

		self.publish_stack = publish_stack
		self.devices = configs['devices']
		self.startWDT()
	
	def startWDT(self):
		time = float('inf')
		for device in self.devices:
			if device['status'] and device['operation_time'] and device['operation_time']['period'] and device['operation_time']['period_steps'][0] == 0:
				if 0 < device['operation_time']['period'] < time:
					time = device['operation_time']['period']
		self.wdt = Watchdog(time * 2 + 10)

	def connect(self):
		while True:
			try:
				while self.publish_stack.length() > 0:
					failed_send = False
					data = json.loads(self.publish_stack.get())
					i = 1
					while i < 9:
						try:
							if 'tries' in data:
								data.update({'tries': data['tries'] + 1})
							else:
								data.update({'tries': 1})
							
							if not 'gateway' in data:
								data.update({'gateway': {'uuid': self.uuid}})

							c = MQTTClient(self.topic, self.ip, self.port, self.user, self.password)
							c.connect()
							c.publish(self.topic, json.dumps(data).encode())
							c.disconnect()

							failed_send = False

							self.wdt.feed()
							break

						except Exception:
							i += 1
							failed_send = True
							time.sleep(5)
					
					# no persistency for ack answer
					if failed_send and data['type'] != 'identification':
						self.publish_stack.write_buffer(json.dumps(data))
					self.publish_stack.delete()

				# TODO: verify necessity of sleep here
			except Exception as e:
				self.publish_stack.delete()
				log("Publish-connect: {}".format(e))
			time.sleep(5)
