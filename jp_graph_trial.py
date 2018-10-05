import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import datetime
import functions as f
import signal
import getopt
import sys
import csv

DATA = "27-09-2018"
PATH = "GT_telefono/27_09/"
DATE =  "27_09.txt"
FUSO_ORARIO = 7188000
OUTPUT_PATH_INFRA_TS = "/home/daniubo/Scrivania/Git/smartGate/analysis/match_analysis/"
OUTPUT_PATH_PIR_TS = "/home/daniubo/Scrivania/Git/smartGate/analysis/match_analysis/"
OUTPUT_PATH_TOF_TS = "/home/daniubo/Scrivania/Git/smartGate/analysis/match_analysis/"

def just_processing(a, b, delta, var, use, TIME):
	use_infra = use[0]
	use_pir = use[1]
	use_camera = use[2]
	do_graph = use[3]
	check_matching = use[4]
	use_tof = use[5]
	span = var
	enough_zero = var
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
		'''
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
		'''
		#print("Lunghezza p1b: ", len(uniform_p1b))

		#pir_mask = f.generate_mask(array_support,uniform_p0a,uniform_p0b,uniform_p1a,uniform_p1b)

		activation_p0a = f.activate(p0a)
		activation_p1a = f.activate(p1a)
		activation_p0b = f.activate(p0b)
		activation_p1b = f.activate(p1b)

		#activation_mask = f.activate(pir_mask)
		if processing:
			#E e U da utilizzare solo se si riescono a mettere i valori rilevati o no dai grafici
			E_a = []
			E_b = []
			U_a = []
			U_b = []
			ins_a, out_a, E_a, U_a = f.count_entries(activation_p1a,activation_p0a,'A', activation_p1b, activation_p0b, delta, span)
			ins_b, out_b, E_b, U_b = f.count_entries(activation_p1b,activation_p0b,'B', activation_p1a, activation_p0a, delta, span)
			'''
			if check_matching:
				with open(OUTPUT_PATH_PIR_TS+"pir_ts.csv", 'a') as match:
					writer = csv.writer(match, delimiter=';')
					writer.writerow(['TS', 'TypeOfEvent'])
					for element in E_a:
						writer.writerow([element, 1])
					for element in U_a:
						writer.writerow([element, 0])
					for element in E_b:
						writer.writerow([element, 3])
					for element in U_b:
						writer.writerow([element, 2])
			'''				
		if processing:
			I_pir = max(ins_a, ins_b);
			O_pir= max(out_a, out_b);

		if do_graph:
			plt.plot(*zip(*p0a), color='green', label='p0a')
			plt.plot(*zip(*p0b), color='orange', label='p0b')
			plt.plot(*zip(*p1a), color='blue', label='p1a')
			plt.plot(*zip(*p1b), color='red', label='p1b')
			plt.plot(E_a, [1.5]*len(E_a), 'ro', color='blue', label='algorithm entries A')
			plt.plot(U_a, [1.5]*len(U_a), 'ro', color='black', label='algorithm exits A')
			plt.plot(E_b, [1.25]*len(E_b), 'rx', color='blue', label='algorithm entries B')
			plt.plot(U_b, [1.25]*len(U_b), 'rx', color='black', label='algorithm exits B')
			plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
			plt.ylim(-0.2, 2)
			plt.show()

	if use_infra:
		activate_infra_1, infrared_a = f.processing_infrared_2(infrared_a, enough_zero)
		activate_infra_0, infrared_b = f.processing_infrared_2(infrared_b, enough_zero)

		uniform_infra_a = f.uniform_list(array_support,infrared_a,min_ts_a,max_ts_a,min_ts,max_ts)
		if (not uniform_infra_a):
			processing = False
			return
		#print("Lunghezza infra_a: ", len(uniform_infra_a))
		uniform_infra_b = f.uniform_list(array_support,infrared_b,min_ts_b,max_ts_b,min_ts,max_ts)
		if (not uniform_infra_b):
			processing = False
			return

		if processing:
			#print("Processo infrarossi\tLunghezza act_1:",len(activate_infra_1),"\tLunghezza act_0:",len(activate_infra_0),"\n")
			E = []
			U = []
			I_inf = 0
			O_inf = 0
			I_inf,O_inf, E_inf, U_inf = f.count_entries_tof(activate_infra_0, activate_infra_1, delta, I_inf, O_inf, E, U)
			print(">>> Infrared:\tIN:",I_inf,"\tO:",O_inf,"\n")
			'''
			if check_matching:
				with open(OUTPUT_PATH_INFRA_TS+"infrared_ts.csv", 'a') as match:
					writer = csv.writer(match, delimiter=';')
					writer.writerow(['TS', 'TypeOfEvent'])
					for element in E:
						writer.writerow([element - min_ts_infra, 1])
					for element in U:
						writer.writerow([element - min_ts_infra, 0])
			'''
		if do_graph:
			# INFRARED
			plt.plot(*zip(*infrared_a), color='green', label ='inf_a')
			plt.plot(*zip(*infrared_b), color='red', label='inf_b')
			plt.plot(E_inf, [1.5]*len(E_inf), 'ro', color='blue', label='algorithm entries INFRA')
			plt.plot(U_inf, [1.5]*len(U_inf), 'ro', color='black', label='algorithm exits INFRA')
			plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
			ylim = (-0.2, 2)
			#plt.title("Infrared")
			plt.show();

	if use_tof:
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

		min_ts_tof = min(tof1[0][0],tof0[0][0])
		max_ts_tof = max(tof1[len(tof1)-1][0],tof0[len(tof0)-1][0])
		interval = int(max_ts-min_ts)

		min_ts_tof0 = tof0[0][0]
		min_ts_tof1 = tof1[0][0]
		max_ts_tof0 = tof0[-1][0]
		max_ts_tof1 = tof1[-1][0]

		array_support = []
		for i in range(0,interval):
			array_support.append(0);

		processing = True
		uniform_tof0 = f.uniform_list_tof(array_support, tof0, min_ts_tof0, max_ts_tof0, min_ts_tof, max_ts_tof)
		if (not uniform_tof0):
			processing = False
			return
		#print("Lunghezza p0a: ", len(uniform_p0a))
		uniform_tof1 = f.uniform_list_tof(array_support, tof1, min_ts_tof1, max_ts_tof1, min_ts_tof, max_ts_tof)
		if (not uniform_tof1):
			processing = False
			return

		lista_ingressi,lista_uscite = f.get_ground_truth(PATH, DATE, DATA, min_ts, max_ts)

		#print("--- Lato 0")
		activation_tof0 = f.activate_tof(uniform_tof0)
		#print("--- Lato 1")
		activation_tof1 = f.activate_tof(uniform_tof1)

		entrate = 0
		uscite = 0
		delta_tof = 1600
		O=0
		I=0
		entrate_act = []
		uscite_act = []
		entrate,uscite, entrate_act, uscite_act = f.count_entries_tof(activation_tof0, activation_tof1, delta_tof, I, O, entrate_act,uscite_act)
		'''
		if check_matching:
			with open(OUTPUT_PATH_TOF_TS+"tof_ts.csv", 'a') as match:
				writer = csv.writer(match, delimiter=';')
				writer.writerow(['TS', 'TypeOfEvent'])
				for element in entrate_act:
					writer.writerow([element + min_ts, 1])
				for element in uscite_act:
					writer.writerow([element + min_ts, 0])
		'''
		print("------- RILEVAZIONI ----------")
		print("Entrate ",entrate,"\nUscite ", uscite)
		if do_graph:
			plt.figure(1, figsize=(15,8))
			plt.plot(lista_ingressi, [10]*len(lista_ingressi), 'ro', color='blue', label='GT entries')
			plt.plot(lista_uscite, [10]*len(lista_uscite), 'ro', color='green', label='GT exits')
			plt.plot(entrate_act, [100]*len(entrate_act), 'ro', color='blue', label='algorithm entries')
			plt.plot(uscite_act, [100]*len(uscite_act), 'ro', color='green', label='algorithm exits')
			plt.plot(uniform_tof1, color='orange', label='Lato 1')
			plt.plot(uniform_tof0, color='red', label='Lato 0')
			#plt.legend(handles=[green_tof,red_tof,alg_entries,alg_exits,true_exits,true_entries])
			plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

			plt.show();

	if check_matching:
		check_in_TOF = []
		check_out_TOF = []
		check_in_INF = []
		check_out_INF = []
		check_TOF = []
		check_INF = []
		for element in entrate_act:
			check_in_TOF.append((element + min_ts_tof))
			check_TOF.append(element + min_ts_tof)
		for element in uscite_act:
			check_out_TOF.append((element + min_ts_tof))
			check_TOF.append(element + min_ts_tof)
		for element in E_inf:
			check_in_INF.append((element))
			check_INF.append(element)
		for element in U_inf:
			check_out_INF.append(element)
			check_INF.append(element)

		check_INF.sort()
		check_TOF.sort()
		plt.plot(check_in_TOF, [1]*len(check_in_TOF),'ro', color='blue', label='IN TOF')
		plt.plot(check_out_TOF, [3]*len(check_out_TOF), 'ro', color='blue', label='OUT TOF')
		plt.plot(check_in_INF, [1.5]*len(check_in_INF), 'rx', color='green', label='IN INF')
		plt.plot(check_out_INF, [3.5]*len(check_out_INF), 'rx', color='green', label='OUT INF')
		plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
		plt.show();
		plt.plot(check_TOF, [1]*len(check_TOF),'ro', color='blue', label='TOF')
		plt.plot(check_INF, [1.5]*len(check_INF), 'rx', color='green', label='INF')
		plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
		plt.ylim(0.5,2)
		plt.show()



	if use_pir and use_infra:				#opzione non contemplata
		return I_pir, O_pir, I_inf, O_inf
	elif use_pir:
		return I_pir, O_pir, min_ts, max_ts
	elif use_infra:
		return I_inf, O_inf, min_ts, max_ts
	elif use_camera:
		print("Nothing to return, camera data processed.\n")
		return 1
	elif use_tof:
		return entrate, uscite, len(lista_ingressi), len(lista_uscite)
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
