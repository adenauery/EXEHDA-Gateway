import json
import time

from main import mcron
from main.driver.init import start as driver_start
from utils import get_configs, get_date, log, get_posix_timestamp

class Scheduler:
	def __init__(self, subscribe_stack, publish_stack):
		mcron.init_timer()
		mcron.remove_all()

		self.subscribe_stack = subscribe_stack
		self.publish_stack = publish_stack
		self.scheduler()

	def callback(self, driver, cb_type, uuid, pin = None, write = None, **kwargs):
		def wrapper(callback_id = None, current_time = None, callback_memory = None):
			try:
				device = driver_start(driver, pin, write)
				device.run()
				if device.read:
					data = {"uuid": uuid, "data": str(device.read), "type": cb_type, "gathered_at": get_date()}
					if kwargs:
						data.update(kwargs)

					self.publish_stack.insert(json.dumps(data))

				if kwargs['scheduling']:
					self.delete_scheduling(kwargs['identifier'])
						
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
			if device['status'] == True and 'operation_time' in device:
				period = device['operation_time']['period']
				if type(period) is int and period is not 0:
					period_steps = set(device['operation_time']['period_steps'])
					pin = device['pin'] if 'pin' in device else None
					self.init_driver(device)
					mcron.insert(period, period_steps, device['uuid'], self.callback(device['driver'], "publication", device['uuid'], pin, None, identifier = None, scheduling = False))
				else:
					log("Scheduler: period of " + device['driver'] + " driver is invalid")
		
		schedules = self.get_schedules()
		for scheduling in schedules:
			must_be_stored = False # it's already persistent
			self.process_scheduling_create(scheduling, configs['devices'], must_be_stored)
	
	def get_schedules(self):
		schedules_file = open('schedules.json', 'a+')
		schedules_str = schedules_file.read()
		schedules_file.close()

		if schedules_str != '':
			schedules = json.loads(schedules_str)
		else:
			schedules = []

		return schedules

	def store_schedules(self, schedules):
		schedules_str = json.dumps(schedules)
		schedules_file = open('schedules.json', 'w+')
		schedules_file.write(schedules_str)
		schedules_file.close()
	
	def store_scheduling(self, scheduling):
		schedules = self.get_schedules()
		schedules.append(scheduling)
		self.store_schedules(schedules)

	def get_scheduling(self, identifier):
		schedules = self.get_schedules()
		index = -1
		for i, scheduling in enumerate(schedules):
			if scheduling['identifier'] == identifier:
				index = i
				break
		
		return [index, schedules]

	def delete_scheduling(self, identifier):
		[index, schedules] = self.get_scheduling(identifier)
		if index != -1:
			mcron.remove(identifier)
			schedules.pop(index)
			self.store_schedules(schedules)
			return True

		return False

	def process_scheduling_update(self, new_scheduling):
		[index, schedules] = self.get_scheduling(new_scheduling['identifier'])
		
		if index != -1:
			must_be_stored = True
			configs = get_configs()
			scheduling = schedules[index]
			
			self.delete_scheduling(new_scheduling['identifier']) # remove old
			scheduling.update(new_scheduling['data'])
			self.process_scheduling_create(scheduling, configs['devices'], must_be_stored) # insert updated 
			
			return json.dumps({"data": "successful update", "type": "scheduling_reply", "gathered_at": get_date(), "identifier": scheduling['identifier']})
		else:
			return json.dumps({"data": "update failed, the scheduling does not exist or has already been processed", "type": "scheduling_reply", "gathered_at": get_date(), "identifier": new_scheduling['identifier']})
	
	def process_scheduling_read(self, scheduling):
		schedules = self.get_schedules()
		return json.dumps({"data": schedules, "type": "scheduling_reply", "gathered_at": get_date(), "identifier": scheduling['identifier']})
	
	def process_scheduling_delete(self, scheduling):
		if self.delete_scheduling(scheduling['identifier']):
			return json.dumps({"data": "successful delete", "type": "scheduling_reply", "gathered_at": get_date(), "identifier": scheduling['identifier']})
		else:
			return json.dumps({"data": "delete failed, the scheduling does not exist or has already been processed", "type": "scheduling_reply", "gathered_at": get_date(), "identifier": scheduling['identifier']})
	
	def process_scheduling_create(self, scheduling, devices, must_be_stored):
		scheduling_timestamp = int(scheduling['timestamp'])
		current_timestamp = get_posix_timestamp()
		if scheduling_timestamp > current_timestamp:
			device = self.get_device(devices, scheduling['uuid'])
			if device:
				write = scheduling['write'] if 'write' in scheduling else None 
				scheduling_time = scheduling_timestamp - current_timestamp
				mcron.insert(scheduling_time, set([0]), scheduling['identifier'], self.callback(device['driver'], "publication", device['uuid'], device['pin'], write, identifier = scheduling['identifier'], scheduling = True))
				if must_be_stored:
					self.store_scheduling(scheduling)
				return json.dumps({"data": "successful", "type": "scheduling_reply", "gathered_at": get_date(), "identifier": scheduling['identifier']})
			else:
				return json.dumps({"data": "json device 'uuid' not found", "type": "scheduling_reply", "gathered_at": get_date(), "identifier": scheduling['identifier']})
		else:
			self.delete_scheduling(scheduling['identifier'])
			return json.dumps({"data": "json 'timestamp' invalid, current_timestamp: " + str(current_timestamp), "type": "scheduling_reply", "gathered_at": get_date(), "identifier": scheduling['identifier']})

	def process_operation(self, data, device):
		reply = None
		
		if device['status'] == True:
			pin = device['pin'] if 'pin' in device else None
			write = data['write'] if 'write' in data else None
			
			# callback already reply
			cb = self.callback(device['driver'], "operation_reply", device['uuid'], pin, write, identifier = data['identifier'], scheduling = False)
			cb()
		else:
			reply = json.dumps({"uuid": device['uuid'], "data": "driver_not_enabled", "type": "operation_reply", "gathered_at": get_date(), "identifier": data['identifier']})
	
		return reply

	def process_acknowledgement(self, configs):
		configs.update({"type": "identification", "gathered_at": get_date()})
		return json.dumps(configs)
	
	def get_device(self, devices, uuid):
		for device in devices:
			if device['uuid'] == uuid:
				return device
		return None

	def start(self):
		log("Scheduler: EXEHDAGateway operating")
		
		configs = get_configs()
		configs.update({"type": "identification", "gathered_at": get_date()})
		self.publish_stack.insert(json.dumps(configs))

		while True:
			try:
				while self.subscribe_stack.length() > 0:
					reply = None
					data = json.loads(self.subscribe_stack.get())
					self.subscribe_stack.delete()
					
					if 'type' in data:	
						subscription_type = data['type']
						configs = get_configs()

						if subscription_type == "acknowledgement":
							reply = self.process_acknowledgement(configs)
							
						elif subscription_type == "operation":
							if 'uuid' in data and 'identifier' in data:
								device = self.get_device(configs['devices'], data['uuid'])
								if device:
									reply = self.process_operation(data, device)
								else:
									reply = json.dumps({"uuid": data['uuid'], "data": "device not found", "type": "operation_reply", "gathered_at": get_date(), "identifier": data['identifier']})
							else:
								reply = json.dumps({"data": "json 'uuid' or 'identifier' field not found", "type": "operation_reply", "gathered_at": get_date()})
						
						elif subscription_type == "scheduling":
							if 'schedules' in data:
								schedules = data['schedules']
								for scheduling in schedules:
									if 'type' in scheduling and 'identifier' in scheduling:
										if scheduling['type'] == "create":
											if 'timestamp' in scheduling and 'uuid' in scheduling:
												must_be_stored = True # enable persistency
												reply = self.process_scheduling_create(scheduling, configs['devices'], must_be_stored)
											else:
												reply = json.dumps({"data": "json 'timestamp' or 'uuid' field not found", "type": "scheduling_reply", "gathered_at": get_date(), "identifier": scheduling['identifier']})
										elif scheduling['type'] == "read":
											reply = self.process_scheduling_read(scheduling)
										elif scheduling['type'] == "update":
											if 'data' in scheduling:
												reply = self.process_scheduling_update(scheduling)
											else:
												reply = json.dumps({"data": "json 'data' field not found", "type": "scheduling_reply", "gathered_at": get_date(), "identifier": scheduling['identifier']})
										elif scheduling['type'] == "delete":
											reply = self.process_scheduling_delete(scheduling)
										else:
											reply = json.dumps({"data": "action: " + scheduling['type'] + " not recognitzed", "type": "scheduling_reply", "gathered_at": get_date(), "identifier": scheduling['identifier']})
									else:
										reply = json.dumps({"data": "json type or identifier field not found", "type": "scheduling_reply", "gathered_at": get_date()})
							else:
								reply = json.dumps({"data": "json 'schedules' field not found", "type": "scheduling_reply", "gathered_at": get_date()})
						else:
							reply = json.dumps({"data": "subscription type error", "type": subscription_type + "_reply", "gathered_at": get_date()})
					else:
						reply = json.dumps({"data": "json 'type' field not found", "type": "reply", "gathered_at": get_date()})
					
					if reply:
						self.publish_stack.insert(reply)

				time.sleep(0.5)
			except Exception as e:
				log("Scheduler: {}".format(e))
				self.subscribe_stack.delete()
