import _thread
import os


class List(object):
	def __init__(self):
		self.list = []
		self.lock = _thread.allocate_lock()
		file = open('buffer.txt', 'w+')

	def insert(self, elem):
		self.lock.acquire()
		try:
			if len(self.list) == 100:
				del self.list[0]
			self.list.append(elem)
		except Exception:
			del self.list[0]
			self.list.append(elem)
		self.lock.release()

	def delete(self):
		self.lock.acquire()
		elem = self.list[0]
		del self.list[0]
		self.lock.release()
		return elem

	def get(self):
		self.lock.acquire()
		elem = self.list[0]
		self.lock.release()
		return elem

	def length(self):
		self.lock.acquire()
		list_length = len(self.list)
		self.lock.release()
		return list_length

	def length_add(self, elem):
		self.lock.acquire()
		if len(self.list) == 0:
			self.lock.release()
			return 0
		else:
			self.list.append(elem)
			self.lock.release()
			return 1

	def write_buffer(self):
		self.lock.acquire()
		file = open('buffer.txt', 'w')
		try:
			while len(self.list) > 0:
				msg = self.list[0]
				del self.list[0]
				file.write(str(msg) + "\n")
		finally:
			file.close()
			self.lock.release()

	def read_buffer(self):
		self.lock.acquire()
		file = open('buffer.txt', 'r')
		try:
			while True:
				line = file.readline().rstrip("\n")
				if len(line) != 0:
					self.list.append(line)
				else:
					break
		finally:
			file.close()
			self.lock.release()

	def write_list_buffer(self):
		self.lock.acquire()
		file = open('buffer.txt', 'w')
		try:
			i = 0
			while i < len(self.list):
				data = self.list[i]
				file.write("{}\n".format(data))
				i += 1
		finally:
			file.close()
			self.lock.release()
