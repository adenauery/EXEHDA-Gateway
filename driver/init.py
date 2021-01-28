import time

from main.driver.gpio import DriverGPIO
from main.driver.ldr import DriverLDR
from main.driver.free_memory import DriverFreeMemory
from main.driver.start_time import DriverStartTime
from main.driver.temperature import DriverTemperature
from main.driver.reset import DriverReset
from main.driver.update import DriverUpdate
from main.driver.upgrade import DriverUpgrade
from utils import log


class Driver(object):
	def __init__(self, strategy, pin=None, write=None):
		self.strategy = strategy

		self.pin = pin
		self.write = write
		self.read = None

	def run(self, i=1):
		try:
			self.read = self.strategy.run(pin=self.pin, write=self.write)
		except NotImplementedError:
			log("Driver: NotImplementedError")
			pass
		except Exception as e:
			if i < 5:
				time.sleep(1)
				self.run(i=i+1)
			else:
				log("Driver: {} - {} - {}".format(e, pin, strategy))


def start(strategy_choice, pin=None, write=None):
	if strategy_choice == "gpio":
		strategy = DriverGPIO()
	elif strategy_choice == "ldr":
		strategy = DriverLDR()
	elif strategy_choice == "free_memory":
		strategy = DriverFreeMemory()
	elif strategy_choice == "start_time":
		strategy = DriverStartTime()
	elif strategy_choice == "temperature":
		strategy = DriverTemperature()
	elif strategy_choice == "update":
		strategy = DriverUpdate()
	elif strategy_choice == "upgrade":
		strategy = DriverUpgrade()
	else:
		raise NotImplementedError
	return Driver(strategy, pin=pin, write=write)
