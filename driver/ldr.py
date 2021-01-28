from main.driver.strategy import DriverStrategy
from machine import Pin, ADC


class DriverLDR(DriverStrategy):
	def run(self, **kwargs):
		sensor = ADC(Pin(kwargs['pin'], Pin.IN))
		return sensor.read()
