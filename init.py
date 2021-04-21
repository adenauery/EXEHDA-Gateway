from _thread import start_new_thread

from main.stack import Stack
from main.mqtt import Subscribe, Publish
from main.scheduler import Scheduler


def start():
	publish_stack = Stack()
	publish_stack.read_buffer()

	subscribe_stack = Stack()

	mqtt_subscribe = Subscribe(subscribe_stack)
	start_new_thread(mqtt_subscribe.connect, ())

	mqtt_publish = Publish(publish_stack)
	start_new_thread(mqtt_publish.connect, ())

	operation_scheduler = Scheduler(subscribe_stack, publish_stack)
	operation_scheduler.start()
