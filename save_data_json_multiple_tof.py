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

#PATH = "/home/cluster/smartGate/"
#PATH = "/home/daniubo/Scrivania/smartGate/"
PATH = "/Users/wunagana/Documents/GitHub/smartGate"

SIZE = 300
DATE = "01_10"


#db = MySQLdb.connect(host="10.79.1.176", user = "root", passwd = "root", db = "smartgateDB_real")
#cursor = db.cursor()

multiple_tof = [];

n_process = 0
count_multiple_tof = 0

topic_sensors_multiple_tof = "smartgate/sg1/mls/multiple_tof"
list_of_dict_multiple_tof = []
dict_multiple_tof = {}


lock = Lock()

flag_a = False

hour = str(datetime.datetime.now().strftime('%H'))
minutes = str(int(str(datetime.datetime.now().strftime('%M'))))
time_file = hour+"_"+minutes

def on_message(client, userdata, message):
		#print("message received, topic: ", message.topic)
		global dict_multiple_tof, list_of_dict_multiple_tof
		global time_file
		global flag_a, flag_b
		if flag_a:
			multiple_tof = copy.deepcopy(list_of_dict_multiple_tof)
			dump_t = Dumping_thread(multiple_tof)
			dump_t.start()
			list_of_dict_multiple_tof = []
			flag_a = False
		if message.topic == topic_sensors_multiple_tof:
			print("M",  end="", flush=True)
			try:
				with lock:
					dict_multiple_tof.update(json.loads(str(message.payload.decode("utf-8"))));
			except ValueError as e:
				print(">>> Errore decodifica: ", e)
				#print("Contenuto pacchetto:\n", str(message.payload.decode("utf-8")))
				return
			dict_multiple_tof['Time'] = int(datetime.datetime.now().strftime("%s"))*1000
			list_of_dict_multiple_tof.append(copy.deepcopy(dict_multiple_tof))

			if(len(list_of_dict_multiple_tof) > SIZE):
				print("|")
				flag_a = True

		else:
			print(">>> Errore\n")

class Subscriber_thread(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.client_name = "localhost"+str(datetime.datetime.now())
		self.broker_address = BROKER_ADDRESS;
		self.topic_sensors_multiple_tof = "smartgate/sg1/mls/multiple_tof"

	def run(self):
		subscriber = mqtt.Client(self.client_name);
		print(">>> Function on message assigned!")
		subscriber.on_message = on_message
		print (">>> Connecting to broker\n")
		subscriber.connect(self.broker_address);
		print (">>> Subscribing to topic:", self.topic_sensors_multiple_tof);
		subscriber.subscribe(self.topic_sensors_multiple_tof);
		print(">>> Subscribed!\n")
		subscriber.loop_forever()

class Processer_thread(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)


	def run(self):
		global dict_multiple_tof, list_of_dict_multiple_tof

		#print (list_of_dict_b)
		print (">>> Thread processing started...")
		with lock:
			with open("side_multiple_tof.json","w") as side_tof0:
				json.dump(list_of_dict_multiple_tof, side_multiple_tof)



		return

class Dumping_thread(threading.Thread):

	def __init__(self, multiple_tof):
		threading.Thread.__init__(self)
		self.multiple_tof = multiple_tof

	def run(self):
		hour = str(datetime.datetime.now().strftime('%H'))
		minutes = str(int(str(datetime.datetime.now().strftime('%M'))))
		time_file = hour+"_"+minutes
		try:
			with open(PATH+"/ground_truth_realistic/"+DATE+"/multiple_tof_"+time_file+".json","w") as side_a:
				json.dump(self.multiple_tof, side_a)
		except TypeError as e:
			print(">>> Errore dump: ", e)

		return

def processing():

	'''
	Elimino dalla lista di dizionari quelli già esaminati
	'''
	global count_multiple_tof
	global n_process
	global list_of_dict_multiple_tof



	if n_process == 0:
		count_multiple_tof = len(list_of_dict_multiple_tof)
		n_process = 1
		print ("Dimensione lista 0: ", len(list_of_dict_multiple_tof))


	else:
		del list_of_dict_multiple_tof[0:count_multiple_tof]

		count_multiple_tof = len(list_of_dict_multiple_tof)

		print ("Dimensione lista: ", len(list_of_dict_multiple_tof))

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
