from main.driver.strategy import DriverStrategy
from machine import Pin
from onewire import OneWire
from ds18x20 import DS18X20


class DriverTemperature(DriverStrategy):
	def run(self, **kwargs):
		ds = DS18X20(OneWire(Pin(kwargs['pin'][0], Pin.IN)))
		sensors = ds.scan()
		ds.convert_temp()
		value = ds.read_temp(sensors[kwargs['pin'][1]])
		return value
