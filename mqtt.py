import json
import time
from json import dumps
from umqtt.simple import MQTTClient
from machine import WDT

from utils import get_configs, log, get_date


class Subscribe:
	def __init__(self, subscribe_list):
		configs = get_configs()

		self.ip = configs['broker_mqtt']['ip']
		self.port = configs['broker_mqtt']['port']
		self.user = configs['broker_mqtt']['user']
		self.password = configs['broker_mqtt']['pass']
		self.topic = bytes("GW_{}".format(configs['gateway']['uuid']), "utf-8")
		self.uuid = configs['gateway']['uuid']

		self.subscribe_list = subscribe_list

	def callback(self, _, msg):
		receive = str(bytes(msg), "utf-8")
		self.subscribe_list.insert(receive)

	def connect(self):
		c = MQTTClient(self.uuid, self.ip, self.port, self.user, self.password, keepalive=120)
		c.set_callback(self.callback)
		c.connect()
		c.subscribe(self.topic)

		try:
			while True:
				if True:
					c.wait_msg()
				else:
					c.check_msg()
					time.sleep(1)
		except Exception as e:
			log("Subscribe: {}".format(e))
			c.disconnect()


class Publish:
	def __init__(self, publish_list):
		configs = get_configs()

		self.ip = configs['broker_mqtt']['ip']
		self.port = configs['broker_mqtt']['port']
		self.user = configs['broker_mqtt']['user']
		self.password = configs['broker_mqtt']['pass']
		self.topic = bytes(configs['broker_mqtt']['topic'], "utf-8")
		self.uuid = configs['gateway']['uuid']

		self.publish_list = publish_list
		self.wdt = WDT(timeout=1000*60*15)

	def connect(self):
		while True:
			tried_send = 0
			while self.publish_list.length() > 0:
				i = 1
				while i < 9:
					try:
						c = MQTTClient(self.topic, self.ip, self.port, self.user, self.password)
						c.connect()

						data = json.loads(self.publish_list.get())
						data.update({'gateway': {'uuid': self.uuid}, 'tries': i})
						c.publish(self.topic, json.dumps(data))
						c.disconnect()

						self.publish_list.delete()
						tried_send = 0

						self.wdt.feed()
						break

					except Exception as e:
						if tried_send == 0:
							log("Publish: {}".format(e))
							tried_send = 1
						i += 1
						time.sleep(5)
			time.sleep(5)
