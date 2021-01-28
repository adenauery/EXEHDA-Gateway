import json
import time

from main import mcron
from main.driver.init import start as driver_start
from utils import get_configs, get_date, log


class Scheduler:
	def __init__(self, subscribe_list, publish_list):
		mcron.init_timer()
		mcron.remove_all()

		self.subscribe_list = subscribe_list
		self.publish_list = publish_list
		self.scheduler()

	def callback(self, driver, cb_type, uuid, pin = None, write = None, **kwargs):
		def wrapper(callback_id = None, current_time = None, callback_memory = None):
			try:
				device = driver_start(driver, pin, write)
				device.run()
				data = {"uuid": uuid, "data": str(device.read), "type": cb_type, "gathered_at": get_date()}

				if kwargs:
					data.update(kwargs)

				self.publish_list.insert(json.dumps(data))
			except Exception as e:
				log("Scheduler-callback: {}".format(e))
		return wrapper
	
	def init_driver(self, device):
		driver = device['driver']
		pin = device['pin'] if 'pin' in device else None
		if driver == "temperature":
			driver_start(driver, pin, None).run()

	def scheduler(self):
		configs = get_configs()
		for device in configs['devices']:
			self.init_driver(device)
			if device['status'] == True:
				period = device['operation_time']['period']
				period_steps = set(device['operation_time']['period_steps'])
				pin = device['pin'] if 'pin' in device else None
				mcron.insert(period, period_steps, device['uuid'], self.callback(device['driver'], "publication", device['uuid'], pin))

	def start(self):
		print("Gateway operando!")
		configs = get_configs()
		configs.update({"type": "identification", "gathered_at": get_date()})
		self.publish_list.insert(json.dumps(configs))

		while True:
			try:
				while self.subscribe_list.length() > 0:
					data = json.loads(self.subscribe_list.get())
					subscription_type = data['type']
					configs = get_configs()

					if subscription_type == "operation":
						device = None
						for d in configs['devices']:
							if d['uuid'] == data['uuid']:
								device = d
								break
						if not device:
							break

						pin = device['pin'] if 'pin' in device else None
						action = data['action'] if 'action' in data else None

						cb = self.callback(device['driver'], "operation_reply", device['uuid'], pin, action, identifier=data['identifier'])
						cb()
					elif subscription_type == "acknowledgement":
						configs.update({"type": "identification", "gathered_at": get_date()})
						self.publish_list.insert(json.dumps(configs))
					else:
						log("Scheduler: subscription type error")

					self.subscribe_list.delete()
				time.sleep(0.5)
			except Exception as e:
				if e == "identifier":
					log("Scheduler: faltando chave identifier")
				else:	
					log("Scheduler: {}".format(e))
				self.subscribe_list.delete()
