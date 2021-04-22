import _thread
import os


class Stack(object):
	def __init__(self):
		self.stack = []
		self.lock = _thread.allocate_lock()

	def insert(self, elem):
		self.lock.acquire()
		try:
			if len(self.stack) == 100:
				del self.stack[0]
			self.stack.append(elem)
		except Exception:
			del self.stack[0]
			self.stack.append(elem)
		self.lock.release()

	def delete(self):
		self.lock.acquire()
		elem = self.stack[0]
		del self.stack[0]
		self.lock.release()
		return elem

	def get(self):
		self.lock.acquire()
		elem = self.stack[0]
		self.lock.release()
		return elem

	def length(self):
		self.lock.acquire()
		stack_length = len(self.stack)
		self.lock.release()
		return stack_length

	def length_add(self, elem):
		self.lock.acquire()
		if len(self.stack) == 0:
			self.lock.release()
			return 0
		else:
			self.stack.append(elem)
			self.lock.release()
			return 1

	def write_buffer(self, data):
		self.lock.acquire()
		file = open('buffer.txt', 'a')
		file.write(data + "\n")
		file.close()
		self.lock.release()

	def clear_buffer(self):
		self.lock.acquire()
		file = open('buffer.txt', 'w')
		file.write('')
		file.close()
		self.lock.release()

	def read_buffer(self):
		self.lock.acquire()
		file = open('buffer.txt', 'r')
		try:
			while True:
				line = file.readline().rstrip("\n")
				if len(line) != 0:
					self.stack.append(line)
				else:
					break
		finally:
			file.close()	
			self.lock.release()

	def write_stack_buffer(self):
		self.lock.acquire()
		file = open('buffer.txt', 'w')
		try:
			while len(self.stack) > 0:
				msg = self.stack[0]
				del self.stack[0]
				file.write(str(msg) + "\n")
		finally:
			file.close()
			self.lock.release()
