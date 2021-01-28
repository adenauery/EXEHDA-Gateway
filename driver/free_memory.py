from main.driver.strategy import DriverStrategy
import gc


class DriverFreeMemory(DriverStrategy):
	def run(self, **kwargs):
		gc.collect()
		return gc.mem_free()
