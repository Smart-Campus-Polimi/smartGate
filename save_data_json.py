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

infrared_a = [];
infrared_b = [];
infrared_mask = [];
analog_a = [];
analog_b = [];
p0a = [];
p1a = [];
p0b = [];
p1b = [];

n_process = 0
count_a = 0
count_b = 0

topic_sensors_a = "smartgate/sg1/mls/sa"
topic_sensors_b = "smartgate/sg1/mls/sb"
topic_camera = "smartgate/sg1/mlc/c"
list_of_dict_a = []
list_of_dict_b = []
list_of_dict_c = []
dict_a = {}
dict_b = {}
dict_c = {}
lock = Lock()
flag_a = False
flag_b = False

hour = str(datetime.datetime.now().strftime('%H'))
minutes = str(int(str(datetime.datetime.now().strftime('%M'))))
time_file = hour+"_"+minutes

def on_message(client, userdata, message):
		#print("message received, topic: ", message.topic)
		global dict_a, list_of_dict_a
		global dict_b, list_of_dict_b
		global dict_c, list_of_dict_c
		global time_file
		global flag_a, flag_b
		if flag_a and flag_b:
			'''
			hour = str(datetime.datetime.now().strftime('%H'))
			minutes = str(int(str(datetime.datetime.now().strftime('%M'))))
			time_file = hour+"_"+minutes
			'''
			a = copy.deepcopy(list_of_dict_a)
			b = copy.deepcopy(list_of_dict_b)
			#c = copy.deepcopy(list_of_dict_c)
			dump_t = Dumping_thread(a, b)
			dump_t.start()
			list_of_dict_a = []
			list_of_dict_b = []
			flag_a = False
			flag_b = False
		if message.topic == topic_sensors_a:
			#print ("Message received on topic: ", topic_sensors_a)
			print("a",  end="", flush=True)
			try:
				with lock:
					dict_a.update(json.loads(str(message.payload.decode("utf-8"))));
			except ValueError as e:
				print(">>> Errore decodifica: ", e)
				#print("Contenuto pacchetto:\n", str(message.payload.decode("utf-8")))
				return
			dict_a['Time'] = int(datetime.datetime.now().strftime("%s"))*1000
			list_of_dict_a.append(copy.deepcopy(dict_a))
			'''
			try:
				with open("/users/wunagana/Documents/GitHub/smartGate/ground_truth_realistic/10_09/side_a_"+time_file+".json","w") as side_a:
					json.dump(list_of_dict_a, side_a)
			except TypeError as e:
				print(">>> Errore dump: ", e)
			'''
			if(len(list_of_dict_a) > 300):
				flag_a = True
		elif message.topic == topic_sensors_b:
			#print ("Message received on topic: ", topic_sensors_b)
			print("b",  end="", flush=True)
			try:
				with lock:
					dict_b.update(json.loads(str(message.payload.decode("utf-8"))));
			except ValueError as e:
				print(">>> Errore decodifica: ", e)
				#print("Contenuto pacchetto:\n", str(message.payload.decode("utf-8")))
				return
			dict_b['Time'] = int(datetime.datetime.now().strftime("%s"))*1000
			list_of_dict_b.append(copy.deepcopy(dict_b))
			'''
			try:
				with open("/users/wunagana/Documents/GitHub/smartGate/ground_truth_realistic/10_09/side_b_"+time_file+".json","w") as side_b:
					json.dump(list_of_dict_b, side_b)
			except TypeError as e:
				print(">>> Errore dump: ", e)
			'''
			if(len(list_of_dict_b) > 300):
				flag_b = True
		elif message.topic == topic_camera:
			#print ("Message received on topic: ", topic_sensors_b)
			print("c",  end="", flush=True)
			try:
				with lock:
					dict_c.update(json.loads(str(message.payload.decode("utf-8"))));
					list_of_dict_c.append(copy.deepcopy(dict_c))
			except ValueError as e:
				print(">>> Errore decodifica: ", e)
				#print("Contenuto pacchetto:\n", str(message.payload.decode("utf-8")))
		else:
			print(">>> Errore\n")




'''
masking analog pir values with digital pir values
'''
'''
def extrapolate_analog(data, activator0, activator1):
	windowed_analog = data
	for i in range(0, len(data)):
		flag = int(activator0[i][1]) or int(activator1[i][1]);
		windowed_analog[i][1] = int(data[i][1]) * flag
	return windowed_analog
'''



class Subscriber_thread(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.client_name = "localhost"+str(datetime.datetime.now())
		self.broker_address = BROKER_ADDRESS;
		self.topic_sensors_a = "smartgate/sg1/mls/sa"
		self.topic_sensors_b = "smartgate/sg1/mls/sb"
		self.topic_camera = topic_camera



	def run(self):
		subscriber = mqtt.Client(self.client_name);
		print(">>> Function on message assigned!")
		subscriber.on_message = on_message
		print (">>> Connecting to broker\n")
		subscriber.connect(self.broker_address);
		print (">>> Subscribing to topic:", self.topic_sensors_a);
		subscriber.subscribe(self.topic_sensors_a);
		print(">>> Subscribed!\n")
		print (">>> Subscribing to topic:", self.topic_sensors_b);
		print(">>> Subscribed!\n")
		subscriber.subscribe(self.topic_sensors_b);
		print (">>> Subscribing to topic:", self.topic_camera);
		print(">>> Subscribed!\n")
		subscriber.subscribe(self.topic_camera);
		subscriber.loop_forever()

class Processer_thread(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)


	def run(self):
		global dict_a, list_of_dict_a
		global dict_b, list_of_dict_b
		global dict_c, list_of_dict_c
		#print (list_of_dict_b)
		print (">>> Thread processing started...")
		with lock:
			with open("side_b.json","w") as side_b:
				json.dump(list_of_dict_b, side_b)
			with open("side_a.json","w") as side_a:
				json.dump(list_of_dict_a, side_a)
			with open("camera.json","w") as cam:
				json.dump(list_of_dict_c, cam)


		return

class Dumping_thread(threading.Thread):

	def __init__(self, a, b):
		threading.Thread.__init__(self)
		self.a = a
		self.b = b

	def run(self):
		hour = str(datetime.datetime.now().strftime('%H'))
		minutes = str(int(str(datetime.datetime.now().strftime('%M'))))
		time_file = hour+"_"+minutes
		try:
			with open("/users/wunagana/Documents/GitHub/smartGate/ground_truth_realistic/13_09/sensors/side_a_"+time_file+".json","w") as side_a:
				json.dump(self.a, side_a)
			except TypeError as e:
				print(">>> Errore dump: ", e)
		try:
			with open("/users/wunagana/Documents/GitHub/smartGate/ground_truth_realistic/13_09/sensors/side_b_"+time_file+".json","w") as side_b:
				json.dump(self.b, side_b)
			except TypeError as e:
				print(">>> Errore dump: ", e)

		return

def processing():

	'''
	Elimino dalla lista di dizionari quelli già esaminati
	'''
	global count_a,count_b, count_c
	global n_process
	global list_of_dict_a
	global list_of_dict_b
	global list_of_dict_c

	if n_process == 0:
		count_a = len(list_of_dict_a)
		count_b = len(list_of_dict_b)
		count_c = len(list_of_dict_c)
		n_process = 1
		print ("Dimensione lista a: ", len(list_of_dict_a))
		print ("Dimensione lista b: ", len(list_of_dict_b))
		print ("Dimensione lista c: ", len(list_of_dict_c))
	else:
		del list_of_dict_a[0:count_a]
		del list_of_dict_b[0:count_b]
		del list_of_dict_c[0:count_c]
		count_a = len(list_of_dict_a)
		count_b = len(list_of_dict_b)
		count_c = len(list_of_dict_c)
		print ("Dimensione lista a: ", len(list_of_dict_a))
		print ("Dimensione lista b: ", len(list_of_dict_b))
		print ("Dimensione lista c: ", len(list_of_dict_c))
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
