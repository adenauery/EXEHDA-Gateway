from main.driver.strategy import DriverStrategy
from machine import Pin


class DriverGPIO(DriverStrategy):
	def run(self, **kwargs):
		sensor = Pin(kwargs['pin'], Pin.OUT)
		sensor.value(kwargs['write'])
		return "successful"
