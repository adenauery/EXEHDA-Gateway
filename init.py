from _thread import start_new_thread

from main.list import List
from main.mqtt import Subscribe, Publish
from main.scheduler import Scheduler


def start():
	publish_list = List()
	publish_list.read_buffer()

	subscribe_list = List()

	mqtt_subscribe = Subscribe(subscribe_list)
	start_new_thread(mqtt_subscribe.connect, ())

	mqtt_publish = Publish(publish_list)
	start_new_thread(mqtt_publish.connect, ())

	operation_scheduler = Scheduler(subscribe_list, publish_list)
	operation_scheduler.start()
