from main.driver.strategy import DriverStrategy


class DriverStartTime(DriverStrategy):
	def run(self, **kwargs):
		file = open('start_time.dat', 'r')
		sensor = file.readline()
		file.close()
		return sensor
