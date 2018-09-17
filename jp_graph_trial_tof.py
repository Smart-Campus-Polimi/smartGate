import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import datetime
import functions as f
import signal
import getopt
import sys

DATA = "11-09-2018"
PATH = "GT_telefono/11_09/"
DATE =  "11_09.txt"
FUSO_ORARIO = 7200000

def just_processing(a, b, TIME):


	'''
	with open('side_a.json') as side_a:
		a = json.load(side_a)
	with open('side_b.json') as side_b:
		b = json.load(side_b)
	'''
	tof0 = [];
	tof1 = [];

	tof0_temp = []
	tof1_temp = []

	for packet in a:
		tof0_temp = packet['TOF']
		number_of_samples = len(tof0_temp);
		time_vector = f.building_time(packet, round(float(1000/number_of_samples)));
		partial_tof0 = [list(a) for a in zip(time_vector, tof0_temp)]
		tof0 = tof0 + partial_tof0;


	for packet in b:
		tof1_temp = packet['TOF']
		number_of_samples = len(tof1_temp);
		time_vector = f.building_time(packet, round(float(1000/number_of_samples)));
		partial_tof1 = [list(b) for b in zip(time_vector, tof1_temp)]
		tof1 = tof1 + partial_tof1;

	tof1 = f.correcting_errors_tof(tof1)
	tof0 = f.correcting_errors_tof(tof0)
	'''
	plt.plot(*zip(*tof1), color='green')
	green_tof = mlines.Line2D([], [], color='green', label='1')
	plt.legend(handles=[green_tof])
	plt.plot(*zip(*tof0), color='red')
	red_tof = mlines.Line2D([], [], color='red', label='0')
	plt.legend(handles=[red_tof])
	plt.show();
	'''

	min_ts = min(tof1[0][0],tof0[0][0])
	max_ts = max(tof1[len(tof1)-1][0],tof0[len(tof0)-1][0])
	#print(tof1[0],tof1[-1])
	#print("############")
	#print(tof0[0],tof0[-1])

	interval = int(max_ts-min_ts)

	min_ts_tof0 = tof0[0][0]
	min_ts_tof1 = tof1[0][0]
	max_ts_tof0 = tof0[-1][0]
	max_ts_tof1 = tof1[-1][0]

	array_support = []
	for i in range(0,interval):
	    array_support.append(0);

	#print("Lunghezza supporto: ", len(array_support))
	processing = True

	uniform_tof0 = f.uniform_list_tof(array_support, tof0, min_ts_tof0, max_ts_tof0, min_ts, max_ts)
	if (not uniform_tof0):
		processing = False
		return
	#print("Lunghezza p0a: ", len(uniform_p0a))
	uniform_tof1 = f.uniform_list_tof(array_support, tof1, min_ts_tof1, max_ts_tof1, min_ts, max_ts)
	if (not uniform_tof1):
		processing = False
		return

	lines = [line.rstrip('\n') for line in open(PATH+DATE)]
	ingresso = []
	lista_ingressi = []
	uscita = []
	lista_uscite = []
	print (max_ts%86400000+FUSO_ORARIO,"<- max ######### min -> ",min_ts%86400000+FUSO_ORARIO)
	for i in lines:
		if i[0] == "I" and i[4:14] == DATA:

			millisecondi = sum(int(x) * 60 ** j for j,x in enumerate(reversed(i[16:24].split(":"))))*1000
			print ("Analisi: ", millisecondi)
			if millisecondi >= (min_ts%86400000 + FUSO_ORARIO) and millisecondi <= ((max_ts%86400000) + FUSO_ORARIO):
				print("I",millisecondi)
				lista_ingressi.append(millisecondi-(min_ts%86400000 + FUSO_ORARIO))
		elif i[0] == "O" and i[5:15] == DATA:
			millisecondi = sum(int(x) * 60 ** j for j,x in enumerate(reversed(i[17:25].split(":"))))*1000
			print ("Analisi: ", millisecondi)
			if millisecondi >= (min_ts%86400000 + FUSO_ORARIO) and millisecondi <= ((max_ts%86400000) + FUSO_ORARIO):
				print("O",millisecondi)
				lista_uscite.append(millisecondi-(min_ts%86400000 + FUSO_ORARIO))

	plt.plot(lista_ingressi, [10]*len(lista_ingressi), 'ro', color='red')
	plt.plot(lista_uscite, [10]*len(lista_uscite), 'ro', color='green')

	plt.plot(uniform_tof1, color='green')
	green_tof = mlines.Line2D([], [], color='green', label='1')
	plt.legend(handles=[green_tof])
	plt.plot(uniform_tof0, color='red')
	red_tof = mlines.Line2D([], [], color='red', label='0')
	plt.legend(handles=[red_tof])
	plt.show();


	activation_tof0 = f.activate_tof(uniform_tof0)
	activation_tof1 = f.activate_tof(uniform_tof1)

	entrate = 0
	uscite = 0
	delta = 1500
	entrate,uscite = f.count_entries_tof(activation_tof0, activation_tof1,delta, min_ts)
	print("Entrate ",entrate," Uscite ", uscite)

	return 0,0
	'''
		#pir_mask = f.generate_mask(array_support,uniform_p0a,uniform_p0b,uniform_p1a,uniform_p1b)

		activation_p0a = f.activate(uniform_p0a)
		activation_p1a = f.activate(uniform_p1a)


		#activation_mask = f.activate(pir_mask)
		if processing:
			ins_a, out_a = f.count_entries(activation_p1a,activation_p0a,'A', activation_p1b, activation_p0b, delta, span)
			ins_b, out_b = f.count_entries(activation_p1b,activation_p0b,'B', activation_p1a, activation_p0a, delta, span)

		if processing:
			I_pir = max(ins_a, ins_b);
			O_pir= max(out_a, out_b);
'''
'''
		if do_graph:
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
			plt.plot(*zip(*ts_in), color='black', marker='o', linestyle='dashed')
			plt.plot(*zip(*ts_out), color='red', marker='x', linestyle='dashed')
			real_in = mlines.Line2D([],[],color='black', label='real_in')
			real_out = mlines.Line2D([],[],color='red', label='real_out')
			plt.legend(handles=[green_pir, orange_pir, blue_pir, red_pir, real_in, real_out])
			plt.title("Real events")
			plt.show()

	if use_infra:
		activate_infra_1, infrared_a = f.processing_infrared_2(infrared_a, enough_zero)
		activate_infra_0, infrared_b = f.processing_infrared_2(infrared_b, enough_zero)
		analog_a = f.convert_list_int(analog_a)
		analog_b = f.convert_list_int(analog_b)

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
		#activate_infra_1 = f.activate_infra(uniform_infra_a)
		#activate_infra_0 = f.activate_infra(uniform_infra_b)

		if processing:
			#print("Processo infrarossi\tLunghezza act_1:",len(activate_infra_1),"\tLunghezza act_0:",len(activate_infra_0),"\n")
			I_inf,O_inf = f.count_infrared(activate_infra_0,activate_infra_1,delta)

		if do_graph:
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
			infrared_a = f.from_ms_to_date(infrared_a)
			infrared_b = f.from_ms_to_date(infrared_b)
			# INFRARED
			plt.plot(*zip(*infrared_a), color='green')
			green_inf = mlines.Line2D([], [], color='green', label='inf_a')
			plt.legend(handles=[green_inf])
			plt.plot(*zip(*infrared_b), color='red')
			red_inf = mlines.Line2D([], [], color='red', label='inf_b')
			# REAL
			plt.plot(*zip(*ts_in), color='black', marker='o', linestyle='dashed')
			plt.plot(*zip(*ts_out), color='orange', marker='x', linestyle='dashed')
			real_in = mlines.Line2D([],[],color='black', label='real_in')
			real_out = mlines.Line2D([],[],color='orange', label='real_out')
			plt.legend(handles=[green_inf, red_inf, real_in, real_out])
			ylim = (-0.2, 2)
			plt.title("Infrared")
			plt.show();


	#print ('################################\nEffective entries: ', I,'\nEffective Exits: ', O,'\n################################')
	print("#")

	if use_pir and use_infra:				#opzione non contemplata
		return I_pir, O_pir, I_inf, O_inf
	elif use_pir:
		return I_pir, O_pir
	elif use_infra:
		return I_inf, O_inf
	elif use_camera:
		print("Nothing to return, camera data processed.\n")
		return 1
	elif do_graph:
		print("Nothing to return, graphs done.\n")
		return 1
	else:
		print("Nothing enabled: NO DATA.\n")
'''
'''
	data = open("all_data.txt", "a")
	data.write('\n################################\nTimestamp: '+ datetime.datetime.now().strftime("%Y-%d-%m %H:%M:%S") +'\nEffective entries: '+str(I)+'\nEffective Exits: '+str(O)+'\n################################\n')
	data.close()
'''
