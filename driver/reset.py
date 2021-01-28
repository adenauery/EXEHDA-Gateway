from main.driver.strategy import DriverStrategy
from machine import reset


class DriverReset(DriverStrategy):
	def run(self, **kwargs):
		reset()
