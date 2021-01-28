from main.driver.strategy import DriverStrategy
from ota import OTA


class DriverUpgrade(DriverStrategy):
	def run(self, **kwargs):
		OTA()
		return True
