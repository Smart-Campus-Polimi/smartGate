'''
Trying to put all togheter and share the resources
'''
import threading
from threading import Lock
import schedule
import json
import paho.mqtt.client as mqtt
import copy
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import datetime
import pprint as pp
from copy import deepcopy
import functions as f
#import MySQLdb
import signal

PACKET_LOSS = 30496000;
BROKER_ADDRESS = "10.79.1.176"

#db = MySQLdb.connect(host="10.79.1.176", user = "root", passwd = "root", db = "smartgateDB_real")
#cursor = db.cursor()


tof0 = [];
tof1 = [];

n_process = 0
count_tof0 = 0
count_tof1 = 0

topic_sensors_tof0 = "smartgate/sg1/mls/tof0"
topic_sensors_tof1 = "smartgate/sg1/mls/tof1"

list_of_dict_tof0 = []
list_of_dict_tof1 = []

dict_tof0 = {}
dict_tof1 = {}

lock = Lock()

flag_a = False
flag_b = False

hour = str(datetime.datetime.now().strftime('%H'))
minutes = str(int(str(datetime.datetime.now().strftime('%M'))))
time_file = hour+"_"+minutes

def on_message(client, userdata, message):
		#print("message received, topic: ", message.topic)
		global dict_tof0, list_of_dict_tof0
		global dict_tof1, list_of_dict_tof1
		global time_file
		global flag_a, flag_b
		if flag_a and flag_b:
			hour = str(datetime.datetime.now().strftime('%H'))
			minutes = str(int(str(datetime.datetime.now().strftime('%M'))))
			time_file = hour+"_"+minutes
			list_of_dict_tof0 = []
			list_of_dict_tof1 = []
			flag_a = False
			flag_b = False
		if message.topic == topic_sensors_tof0:
			#print ("Message received on topic: ", topic_sensors_a)
			print("0",  end="", flush=True)
			try:
				with lock:
					dict_tof0.update(json.loads(str(message.payload.decode("utf-8"))));
			except ValueError as e:
				print(">>> Errore decodifica: ", e)
				#print("Contenuto pacchetto:\n", str(message.payload.decode("utf-8")))
				return
			dict_tof0['Time'] = int(datetime.datetime.now().strftime("%s"))*1000
			list_of_dict_tof0.append(copy.deepcopy(dict_tof0))
			try:
				with open("/users/wunagana/Documents/GitHub/smartGate/ground_truth_realistic/10_09/tof0_"+time_file+".json","w") as side_a:
					json.dump(list_of_dict_tof0, side_a)
			except TypeError as e:
				print(">>> Errore dump: ", e)
			if(len(list_of_dict_tof0) > 300):
				flag_a = True
		elif message.topic == topic_sensors_tof1:
			#print ("Message received on topic: ", topic_sensors_b)
			print("1",  end="", flush=True)
			try:
				with lock:
					dict_tof1.update(json.loads(str(message.payload.decode("utf-8"))));
			except ValueError as e:
				print(">>> Errore decodifica: ", e)
				#print("Contenuto pacchetto:\n", str(message.payload.decode("utf-8")))
				return
			dict_tof1['Time'] = int(datetime.datetime.now().strftime("%s"))*1000
			list_of_dict_tof1.append(copy.deepcopy(dict_tof1))
			try:
				with open("/users/wunagana/Documents/GitHub/smartGate/ground_truth_realistic/10_09/tof1_"+time_file+".json","w") as side_b:
					json.dump(list_of_dict_tof1, side_b)
			except TypeError as e:
				print(">>> Errore dump: ", e)
			if(len(list_of_dict_tof1) > 300):
				flag_b = True
		else:
			print(">>> Errore\n")

class Subscriber_thread(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.client_name = "localhost"+str(datetime.datetime.now())
		self.broker_address = BROKER_ADDRESS;
		self.topic_sensors_tof0 = "smartgate/sg1/mls/tof0"
		self.topic_sensors_tof1 = "smartgate/sg1/mls/tof1"



	def run(self):
		subscriber = mqtt.Client(self.client_name);
		print(">>> Function on message assigned!")
		subscriber.on_message = on_message
		print (">>> Connecting to broker\n")
		subscriber.connect(self.broker_address);
		print (">>> Subscribing to topic:", self.topic_sensors_tof0);
		subscriber.subscribe(self.topic_sensors_tof0);
		print(">>> Subscribed!\n")
		print (">>> Subscribing to topic:", self.topic_sensors_tof1);
		print(">>> Subscribed!\n")
		subscriber.subscribe(self.topic_sensors_tof1);
		subscriber.loop_forever()

class Processer_thread(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)


	def run(self):
		global dict_tof0, list_of_dict_tof0
		global dict_tof1, list_of_dict_tof1

		#print (list_of_dict_b)
		print (">>> Thread processing started...")
		with lock:
			with open("side_tof1.json","w") as side_tof1:
				json.dump(list_of_dict_b, side_tof1)
			with open("side_tof0.json","w") as side_tof0:
				json.dump(list_of_dict_tof0, side_tof0)



		return

def processing():

	'''
	Elimino dalla lista di dizionari quelli già esaminati
	'''
	global count_tof0,count_tof1
	global n_process
	global list_of_dict_tof0
	global list_of_dict_tof1


	if n_process == 0:
		count_tof0 = len(list_of_dict_tof0)
		count_tof1 = len(list_of_dict_tof1)

		n_process = 1
		print ("Dimensione lista 0: ", len(list_of_dict_tof0))
		print ("Dimensione lista 1: ", len(list_of_dict_tof1))

	else:
		del list_of_dict_tof0[0:count_tof0]
		del list_of_dict_tof1[0:count_tof1]
		count_tof0 = len(list_of_dict_tof0)
		count_tof1 = len(list_of_dict_tof1)
		print ("Dimensione lista a: ", len(list_of_dict_tof0))
		print ("Dimensione lista b: ", len(list_of_dict_tof1))
	proc = Processer_thread()
	proc.start()

def subscribe():
	sub = Subscriber_thread();
	sub.setDaemon(True)
	sub.start()

def main():
	subscribe()

	while True:
		schedule.run_pending()


if __name__ == '__main__':
	signal.signal(signal.SIGINT, f.signal_handler)
	main()
