import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import datetime
import functions as f
import signal
import getopt
import sys


def just_processing(a, b, delta, var, use, TIME):
	use_infra = use[0]
	use_pir = use[1]
	use_camera = use[2]
	do_graph = use[3]
	span = var
	enough_zero = var
	#use_anal = use[3]

	'''
	with open('side_a.json') as side_a:
		a = json.load(side_a)
	with open('side_b.json') as side_b:
		b = json.load(side_b)
	'''
	infrared_a = [];
	infrared_b = [];
	infrared_mask = [];
	#analog_a = [];
	#analog_b = [];
	p0a = [];
	p1a = [];
	p0b = [];
	p1b = [];
	#f.correcting_errors(a);
	#f.correcting_errors(b);
	p0a_temp = []
	p1a_temp = []
	infrared_temp_a = []
	#analog_temp_a = []
	p0b_temp = []
	p1b_temp = []
	infrared_temp_b = []
	#analog_temp_b = []

	if use_camera:

		in_people = 0
		out_people = 0
		timestamp_list = []
		for packet in c:
			in_people = in_people + packet['In']
			out_people = out_people + packet['Out']
			timestamp_list.append(packet['Timestamp'])
		print("Camera:\tIn:", in_people, "\tOut: ", out_people)


	for packet in a:
		p0a_temp = packet['P0A']
		p1a_temp = packet['P1A']
		infrared_temp_a = packet['IR']
		#analog_temp_a = packet['AN']

		if (len(p0a_temp) == len(p1a_temp) and len(p0a_temp) == len(infrared_temp_a)):
				number_of_samples = len(p0a_temp)
		else:
			print("\n\n>>> Lunghezze liste lato a differenti!!\n\n")
		number_of_samples = len(infrared_temp_a);
		#print("Numero campioni: ",number_of_samples)
		time_vector = f.building_time(packet, round(float(1000/number_of_samples)));
		partial_infrared_a = [list(a) for a in zip(time_vector, infrared_temp_a)]
		#partial_analog_a = [list(a) for a in zip(time_vector, analog_temp_a)]
		infrared_a = infrared_a + partial_infrared_a;
		#analog_a = analog_a + partial_analog_a;
		p0a_partial = [list(a) for a in zip(time_vector, p0a_temp)]
		p0a = p0a + p0a_partial
		p1a_partial = [list(a) for a in zip(time_vector, p1a_temp)]
		p1a = p1a + p1a_partial

	for packet in b:
		p0b_temp = packet['P0B']
		p1b_temp = packet['P1B']
		infrared_temp_b = packet['IR']
		#analog_temp_b = packet['AN']

		if (len(p0b_temp) == len(p1b_temp) and len(p0b_temp) == len(infrared_temp_b)):
	 		number_of_samples = len(p0b_temp)
		else:
			print("\n\n>>> Lunghezze liste lato b differenti!!\n\n")

		number_of_samples = len(infrared_temp_b);
		#print("Numero campioni b:", number_of_samples)
		time_vector = f.building_time(packet, round(float(1000/number_of_samples)));
		#partial_analog_b = [list(a) for a in zip(time_vector, analog_temp_b)]
		partial_infrared_b = [list(a) for a in zip(time_vector, infrared_temp_b)]
		infrared_b = infrared_b + partial_infrared_b;
		#analog_b = analog_b + partial_analog_b;
		p0b_partial = [list(a) for a in zip(time_vector, p0b_temp)]
		p0b = p0b + p0b_partial
		p1b_partial = [list(a) for a in zip(time_vector, p1b_temp)]
		p1b = p1b + p1b_partial


	min_ts = min(p0b[0][0],p0a[0][0],p1a[0][0],p1b[0][0])
	max_ts = max(p0b[len(p0b)-1][0],p0a[len(p0a)-1][0],p1b[len(p1b)-1][0],p1a[len(p1a)-1][0])
	min_ts_infra = min(infrared_a[0][0],infrared_b[0][0])
	max_ts_infra = max(infrared_a[len(infrared_a)-1][0],infrared_b[len(infrared_b)-1][0])
	#print("Max ts pir: ", max_ts, "\tMax ts infra: ", max_ts_infra,"\n")
	#print("min ts pir: ", min_ts, "\tmin ts infra: ", min_ts_infra,"\n")
	interval = int(max_ts-min_ts)

	min_ts_a = min(p0a[0][0],p1a[0][0])
	min_ts_b = min(p0b[0][0],p1b[0][0])
	max_ts_a = p0a[-1][0]
	max_ts_b = p0b[-1][0]

	min_ts_side = min(min_ts_a, min_ts_b)
	max_ts_side = max(max_ts_a, max_ts_b)

	#interval = int(max_ts-min_ts)
	array_support = []
	for i in range(0,interval):
	    array_support.append(0);
	#print("Lunghezza supporto: ", len(array_support))

	processing = True

	if use_pir:
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

		#pir_mask = f.generate_mask(array_support,uniform_p0a,uniform_p0b,uniform_p1a,uniform_p1b)

		activation_p0a = f.activate(uniform_p0a)
		activation_p1a = f.activate(uniform_p1a)
		activation_p0b = f.activate(uniform_p0b)
		activation_p1b = f.activate(uniform_p1b)

		#activation_mask = f.activate(pir_mask)
		if processing:
			ins_a, out_a = f.count_entries(activation_p1a,activation_p0a,'A', activation_p1b, activation_p0b, delta, span)
			ins_b, out_b = f.count_entries(activation_p1b,activation_p0b,'B', activation_p1a, activation_p0a, delta, span)

		if processing:
			I_pir = max(ins_a, ins_b);
			O_pir= max(out_a, out_b);

		if do_graph:
			'''
			#GRAPH BUILDER
			ts_array = np.loadtxt("/home/daniubo/Scrivania/smartGate/appTS/ts_"+TIME+"_csv.csv", dtype = int, delimiter = ",", skiprows=1)
			ts_in = []
			ts_out = []
			for element in ts_array:
				if element[1] == 1:
					ts_in.append([element[0], 1.2])
				elif element[2] == 1:
					ts_out.append([element[0], 1.2])
			ts_in = f.from_ms_to_date(ts_in)
			ts_out = f.from_ms_to_date(ts_out)
			#print("Qui aggiungere codice per grafici")
			'''
			p0a = f.from_ms_to_date(p0a)
			p0b = f.from_ms_to_date(p0b)
			p1a = f.from_ms_to_date(p1a)
			p1b = f.from_ms_to_date(p1b)
			plt.plot(*zip(*p0a), color='green')
			plt.plot(*zip(*p0b), color='orange')
			plt.plot(*zip(*p1a), color='blue')
			plt.plot(*zip(*p1b), color='red')
			plt.ylim(-0.2, 2)
			green_pir = mlines.Line2D([],[],color='green', label='p0a')
			orange_pir = mlines.Line2D([],[],color='orange', label='p0b')
			blue_pir = mlines.Line2D([],[],color='blue', label='p1a')
			red_pir = mlines.Line2D([],[],color='red', label='p1b')
			'''
			plt.plot(*zip(*ts_in), color='black', marker='o', linestyle='dashed')
			plt.plot(*zip(*ts_out), color='red', marker='x', linestyle='dashed')
			real_in = mlines.Line2D([],[],color='black', label='real_in')
			real_out = mlines.Line2D([],[],color='red', label='real_out')
			plt.legend(handles=[green_pir, orange_pir, blue_pir, red_pir, real_in, real_out])
			'''
			plt.title("Real events")
			plt.show()

	if use_infra:
		activate_infra_1, infrared_a = f.processing_infrared_2(infrared_a, enough_zero)
		activate_infra_0, infrared_b = f.processing_infrared_2(infrared_b, enough_zero)
		#analog_a = f.convert_list_int(analog_a)
		#analog_b = f.convert_list_int(analog_b)

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
		'''
		uniform_analog_a = f.uniform_list(array_support,analog_a,min_ts_a,max_ts_a,min_ts,max_ts)
		if (not uniform_analog_a):
			processing = False
			return
		#print("Lunghezza analog_a: ", len(uniform_analog_a))
		uniform_analog_b = f.uniform_list(array_support,analog_b,min_ts_b,max_ts_b,min_ts,max_ts)
		if (not uniform_analog_b):
			processing = False
			return
		'''
		#print("Lunghezza analog_b: ", len(uniform_analog_b))
		#activate_infra_1 = f.activate_infra(uniform_infra_a)
		#activate_infra_0 = f.activate_infra(uniform_infra_b)

		if processing:
			#print("Processo infrarossi\tLunghezza act_1:",len(activate_infra_1),"\tLunghezza act_0:",len(activate_infra_0),"\n")
			I_inf,O_inf = f.count_infrared(activate_infra_0,activate_infra_1,delta)

		if do_graph:
			'''
			ts_array = np.loadtxt("/home/daniubo/Scrivania/smartGate/appTS/ts_"+TIME+"_csv.csv", dtype = int, delimiter = ",", skiprows=1)
			ts_in = []
			ts_out = []
			for element in ts_array:
				if element[1] == 1:
					ts_in.append([element[0], 1.2])
				elif element[2] == 1:
					ts_out.append([element[0], 1.2])
			ts_in = f.from_ms_to_date(ts_in)
			ts_out = f.from_ms_to_date(ts_out)
			'''
			infrared_a = f.from_ms_to_date(infrared_a)
			infrared_b = f.from_ms_to_date(infrared_b)
			# INFRARED
			plt.plot(*zip(*infrared_a), color='green')
			green_inf = mlines.Line2D([], [], color='green', label='inf_a')
			plt.plot(*zip(*infrared_b), color='red')
			red_inf = mlines.Line2D([], [], color='red', label='inf_b')
			plt.legend(handles=[green_inf, red_inf])
			'''
			# REAL
			plt.plot(*zip(*ts_in), color='black', marker='o', linestyle='dashed')
			plt.plot(*zip(*ts_out), color='orange', marker='x', linestyle='dashed')
			real_in = mlines.Line2D([],[],color='black', label='real_in')
			real_out = mlines.Line2D([],[],color='orange', label='real_out')
			plt.legend(handles=[green_inf, red_inf, real_in, real_out])
			'''
			ylim = (-0.2, 2)
			plt.title("Infrared")
			plt.show();


	#print ('################################\nEffective entries: ', I,'\nEffective Exits: ', O,'\n################################')
	print("#")

	if use_pir and use_infra:				#opzione non contemplata
		return I_pir, O_pir, I_inf, O_inf
	elif use_pir:
		return I_pir, O_pir, min_ts, max_ts
	elif use_infra:
		return I_inf, O_inf, min_ts, max_ts
	elif use_camera:
		print("Nothing to return, camera data processed.\n")
		return 1
	elif do_graph:
		print("Nothing to return, graphs done.\n")
		return 1
	else:
		print("Nothing enabled: NO DATA.\n")
	'''
	data = open("all_data.txt", "a")
	data.write('\n################################\nTimestamp: '+ datetime.datetime.now().strftime("%Y-%d-%m %H:%M:%S") +'\nEffective entries: '+str(I)+'\nEffective Exits: '+str(O)+'\n################################\n')
	data.close()
	'''
