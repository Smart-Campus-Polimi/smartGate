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
import MySQLdb
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
list_of_dict_a = []
list_of_dict_b = []
dict_a = {}
dict_b = {}
lock = Lock()

def on_message(client, userdata, message):
		#print("message received, topic: ", message.topic)
		global dict_a, list_of_dict_a
		global dict_b, list_of_dict_b
		if message.topic == topic_sensors_a:
			#print ("Message received on topic: ", topic_sensors_a)
			print("a",  end="", flush=True)
			try:
				with lock:
					dict_a.update(json.loads(str(message.payload.decode("utf-8"))));
					dict_a['Time'] = int(datetime.datetime.now().strftime("%s"))*1000
					#print("\na: ",int(datetime.datetime.now().strftime("%s"))*1000)
					list_of_dict_a.append(copy.deepcopy(dict_a))
			except ValueError as e:
				print(">>> Errore decodifica")
				print(e)
				#print("Contenuto pacchetto:\n", str(message.payload.decode("utf-8")))
		elif message.topic == topic_sensors_b:
			#print ("Message received on topic: ", topic_sensors_b)
			print("b",  end="", flush=True)
			try:
				with lock:
					dict_b.update(json.loads(str(message.payload.decode("utf-8"))));
					dict_b['Time'] = int(datetime.datetime.now().strftime("%s"))*1000
					#print("\nb: ",int(datetime.datetime.now().strftime("%s"))*1000)
					list_of_dict_b.append(copy.deepcopy(dict_b))
			except ValueError as e:
				print(">>> Errore decodifica")
				print(e)
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
		subscriber.loop_forever()

class Processer_thread(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)


	def run(self):
		global dict_a, list_of_dict_a
		global dict_b, list_of_dict_b
		#print (list_of_dict_b)
		print (">>> Thread processing started...")
		with lock:
			with open("side_b_18_07.json","a") as side_b:
				json.dump(list_of_dict_b, side_b)
			with open("side_a_18_07.json","a") as side_a:
				json.dump(list_of_dict_a, side_a)
		'''
		a = copy.deepcopy(list_of_dict_a)
		b = copy.deepcopy(list_of_dict_b)
		list_of_dict_a = []
		list_of_dict_b = []
		'''
		'''
		with open('side_a.json') as side_a:
		   	a = json.load(side_a)

		with open('side_b.json') as side_b:
			b = json.load(side_b)
		'''

		'''
		removing timestamp where the ntp packet is not received
		'''
		'''
		f.correcting_errors(a);
		f.correcting_errors(b);
		p0a_temp = []
		p1a_temp = []
		infrared_temp_a = []
		analog_temp_a = []
		p0b_temp = []
		p1b_temp = []
		infrared_temp_b = []
		analog_temp_b = []

		for packet in a:
			global infrared_a, analog_a, p0a, p1a;
			p0a_temp = packet['P0A']
			p1a_temp = packet['P1A']
			infrared_temp_a = packet['IR']
			analog_temp_a = packet['AN']

			if (len(p0a_temp) == len(p1a_temp) and len(p0a_temp) == len(infrared_temp_a) and len(p0a_temp) == len(analog_temp_a)):
		 		number_of_samples = len(analog_temp_a)
			else:
				print("\n\n>>> Lunghezze liste lato a differenti!!\n\n")
			number_of_samples = len(infrared_temp_a);
			#print("Numero campioni: ",number_of_samples)
			time_vector = f.building_time(packet, round(float(1000/number_of_samples)));
			partial_infrared_a = [list(a) for a in zip(time_vector, infrared_temp_a)]
			partial_analog_a = [list(a) for a in zip(time_vector, analog_temp_a)]
			infrared_a = infrared_a + partial_infrared_a;
			analog_a = analog_a + partial_analog_a;
			p0a_partial = [list(a) for a in zip(time_vector, p0a_temp)]
			p0a = p0a + p0a_partial
			p1a_partial = [list(a) for a in zip(time_vector, p1a_temp)]
			p1a = p1a + p1a_partial

		for packet in b:
			global infrared_b, analog_b, p0b, p1b;
			p0b_temp = packet['P0B']
			p1b_temp = packet['P1B']
			infrared_temp_b = packet['IR']
			analog_temp_b = packet['AN'] 

			if (len(p0b_temp) == len(p1b_temp) and len(p0b_temp) == len(infrared_temp_b) and len(p0b_temp) == len(analog_temp_b)):
		 		number_of_samples = len(analog_temp_b)
			else:
				print("\n\n>>> Lunghezze liste lato b differenti!!\n\n")

			number_of_samples = len(analog_temp_b);
			#print("Numero campioni b:", number_of_samples)
			time_vector = f.building_time(packet, round(float(1000/number_of_samples)));
			partial_analog_b = [list(a) for a in zip(time_vector, analog_temp_b)]
			partial_infrared_b = [list(a) for a in zip(time_vector, infrared_temp_b)]
			infrared_b = infrared_b + partial_infrared_b;
			analog_b = analog_b + partial_analog_b;
			p0b_partial = [list(a) for a in zip(time_vector, p0b_temp)]
			p0b = p0b + p0b_partial
			p1b_partial = [list(a) for a in zip(time_vector, p1b_temp)]
			p1b = p1b + p1b_partial

		try:
			min_ts = min(p0b[0][0],p0a[0][0],p1a[0][0],p1b[0][0])
			max_ts = max(p0b[len(p0b)-1][0],p0a[len(p0a)-1][0],p1b[len(p1b)-1][0],p1a[len(p1a)-1][0])
		

			interval = int(max_ts-min_ts)

			min_ts_a = min(p0a[0][0],p1a[0][0])
			min_ts_b = min(p0b[0][0],p1b[0][0])
			max_ts_a = p0a[-1][0]
			max_ts_b = p0b[-1][0]

		except IndexError as e_indx:
			print("Dimensione p0a: ", len(p0a))
			print("Dimensione p0b: ", len(p0b))
			print("Dimensione p1a: ", len(p1a))
			print("Dimensione p1b: ", len(p1b))

			print(e_indx)
			print("chiudo il thread")

			#skip this thread
			return

		min_ts_side = min(min_ts_a, min_ts_b)
		max_ts_side = max(max_ts_a, max_ts_b)
		

		#interval = int(max_ts-min_ts)
		array_support = []
		for i in range(0,interval):
		    array_support.append(0);
		#print("Lunghezza supporto: ", len(array_support))
		infrared_a = f.processing_infrared(infrared_a)
		infrared_b = f.processing_infrared(infrared_b)
		analog_a = f.convert_list_int(analog_a)
		analog_b = f.convert_list_int(analog_b)

		processing = True

		uniform_p0a = f.uniform_list(array_support, p0a,min_ts_a,max_ts_a,min_ts,max_ts)
		if (not uniform_p0a):
			processing = False
			return
		#print("Lunghezza p0a: ", len(uniform_p0a))
		uniform_p0b = f.uniform_list(array_support,p0b,min_ts_b,max_ts_b,min_ts,max_ts)
		if (not uniform_p0b):
			processing = False
			return
		#print("Lunghezza p0b: ", len(uniform_p0b))
		uniform_p1a = f.uniform_list(array_support,p1a,min_ts_a,max_ts_a,min_ts,max_ts)
		if (not uniform_p1a):
			processing = False
			return
		#print("Lunghezza p1a: ", len(uniform_p1a))
		uniform_p1b = f.uniform_list(array_support,p1b,min_ts_b,max_ts_b,min_ts,max_ts)
		if (not uniform_p1b):
			processing = False
			return
		#print("Lunghezza p1b: ", len(uniform_p1b))
		uniform_infra_a = f.uniform_list(array_support,infrared_a,min_ts_a,max_ts_a,min_ts,max_ts)
		if (not uniform_infra_a):
			processing = False
			return
		#print("Lunghezza infra_a: ", len(uniform_infra_a))
		uniform_infra_b = f.uniform_list(array_support,infrared_b,min_ts_b,max_ts_b,min_ts,max_ts)
		if (not uniform_infra_b):
			processing = False
			return
		#print("Lunghezza infrared_b: ", len(uniform_infra_b))
		uniform_analog_a = f.uniform_list(array_support,analog_a,min_ts_a,max_ts_a,min_ts,max_ts)
		if (not uniform_analog_a):
			processing = False
			return
		#print("Lunghezza analog_a: ", len(uniform_analog_a))
		uniform_analog_b = f.uniform_list(array_support,analog_b,min_ts_b,max_ts_b,min_ts,max_ts)
		if (not uniform_analog_b):
			processing = False
			return
		#print("Lunghezza analog_b: ", len(uniform_analog_b))

		pir_mask = f.generate_mask(array_support,uniform_p0a,uniform_p0b,uniform_p1a,uniform_p1b)

		activation_p0a = f.activate(uniform_p0a)
		activation_p1a = f.activate(uniform_p1a)
		activation_p0b = f.activate(uniform_p0b)
		activation_p1b = f.activate(uniform_p1b)
		#print("act p0a:", activation_p0a)

		activate_infra_1 = f.activate(uniform_infra_a)
		activate_infra_0 = f.activate(uniform_infra_b)
		'''
		'''
		plt.plot(uniform_infra_a, color='blue');
		plt.plot(uniform_infra_b, color='red');
		#blue_an = mlines.Line2D([], [], color='blue', label='Infrared');
		#plt.legend(handles=[blue_an])
		plt.show();
		'''
		'''
		activation_mask = f.activate(pir_mask)
		if processing:
			ins_a, out_a = f.count_entries(activation_p1a,activation_p0a,'A', activation_p1b, activation_p0b, activate_infra_0, activate_infra_1)
			ins_b, out_b = f.count_entries(activation_p1b,activation_p0b,'B', activation_p1a, activation_p0a, activate_infra_0, activate_infra_1)
		'''
		'''
		pulisco liste già analizzate in count entries,
		'''
		'''
		activation_p0a = []
		activation_p1a = []
		activation_p0b = []
		activation_p1b = []
		activate_infra_a = []
		activate_infra_b = []
		activation_mask = []
		infrared_a = [];
		infrared_b = [];
		infrared_mask = [];
		analog_a = [];
		analog_b = [];
		p0a = [];
		p1a = [];
		p0b = [];
		p1b = [];

		if processing:
			I = max(ins_a, ins_b);
			O = max(out_a, out_b);

		print ('################################\nEffective entries: ', I,'\nEffective Exits: ', O,'\n################################')
		data = open("all_data.txt", "a")
		data.write('\n################################\nTimestamp: '+ datetime.datetime.now().strftime("%Y-%d-%m %H:%M:%S") +'\nEffective entries: '+str(I)+'\nEffective Exits: '+str(O)+'\n################################\n')
		data.close()
		#query = "INSERT INTO smartgateDB_real.flux_giorno (TimeStamp, Gate, Inside, Outside) VALUES ('"+datetime.datetime.now().strftime("%Y-%d-%m %H:%M:%S")+"', '0', '"+str(I)+"', '"+str(O)+"')"
		#cursor.execute(query)
		'''
		'''
		plt.plot(*zip(*p0b), color='green');
		plt.plot(*zip(*p1b), color='orange');
		plt.ylim(-0.2, 1.2)
		green_pir = mlines.Line2D([], [], color='green', label='P0B')
		orange_pir = mlines.Line2D([], [], color='orange', label='P1B')
		plt.legend(handles=[green_pir, orange_pir])
		plt.title("Pir b-side")
		plt.show();

		plt.plot(*zip(*windowed_analog), color='blue');
		blue_an = mlines.Line2D([], [], color='blue', label='Analog');
		plt.yticks(np.arange(0, 1024, 50))
		plt.legend(handles=[blue_an])
		plt.title("Analog")
		plt.show();

		plt.plot(*zip(*p0a), color='green');
		plt.plot(*zip(*p1a), color='orange');
		plt.ylim(-0.2, 1.2)
		green_pir = mlines.Line2D([], [], color='green', label='P0A')
		orange_pir = mlines.Line2D([], [], color='orange', label='P1A')
		plt.legend(handles=[green_pir, orange_pir])
		plt.title("Pir a-side")
		plt.show();

		plt.plot(*zip(*infrared), color='blue');
		blue_an = mlines.Line2D([], [], color='blue', label='Infrared');
		plt.legend(handles=[blue_an])
		plt.show();

		plt.plot(*zip(*p0b), color='green');
		plt.plot(*zip(*p1b), color='orange');
		plt.plot(*zip(*p0a), color='red');
		plt.plot(*zip(*p1a), color='blue');
		plt.ylim(-0.2, 1.2)
		green_pir = mlines.Line2D([], [], color='green', label='P0B')
		orange_pir = mlines.Line2D([], [], color='orange', label='P1B')
		red_pir = mlines.Line2D([], [], color='red', label='P0A')
		blue_pir = mlines.Line2D([], [], color='blue', label='P1A')
		plt.legend(handles=[green_pir, orange_pir, red_pir, blue_pir])
		plt.show()
		'''

		return


def processing():

	'''
	Elimino dalla lista di dizionari quelli già esaminati
	'''
	global count_a,count_b
	global n_process
	global list_of_dict_a
	global list_of_dict_b
	'''
	if n_process == 0:
		count_a = len(list_of_dict_a)
		count_b = len(list_of_dict_b)
		n_process = 1
		print ("\n\nDimensione lista a: ", len(list_of_dict_a))
		print ("Dimensione lista b: ", len(list_of_dict_b))
	else:
		del list_of_dict_a[0:count_a]
		del list_of_dict_b[0:count_b]
		count_a = len(list_of_dict_a)
		count_b = len(list_of_dict_b)
		print ("Dimensione lista a: ", len(list_of_dict_a))
		print ("Dimensione lista b: ", len(list_of_dict_b))
	'''
	proc = Processer_thread()
	proc.start()

def subscribe():
	sub = Subscriber_thread();
	sub.setDaemon(True)
	sub.start()

def main():
	hour = str(datetime.datetime.now().strftime('%H'))
	minutes = str(int(str(datetime.datetime.now().strftime('%M')))+1)
	time_string = hour+":"+minutes

	schedule.every().day.at(time_string).do(subscribe);
	schedule.every(60).minutes.do(processing);

	while True:
		schedule.run_pending()


if __name__ == '__main__':
	signal.signal(signal.SIGINT, f.signal_handler)
	main()