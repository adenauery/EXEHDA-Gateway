from main.driver.strategy import DriverStrategy


class DriverUpdate(DriverStrategy):
	def run(self, **kwargs):
		file = open('configs.json', 'w')
		file.write(kwargs['write'])
		file.close()
		return True
