import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import datetime
import functions as f
import signal
import getopt
import sys

DATA = "24-09-2018"
PATH = "GT_telefono/24_09/"
DATE =  "24_09.txt"
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

	lista_ingressi,lista_uscite = f.get_ground_truth(PATH, DATE, DATA, min_ts, max_ts)



	activation_tof0 = f.activate_tof(uniform_tof0)
	activation_tof1 = f.activate_tof(uniform_tof1)

	entrate = 0
	uscite = 0
	delta = 1600
	O=0
	I=0
	entrate_act = []
	uscite_act = []
	entrate,uscite, entrate_act, uscite_act = f.count_entries_tof(activation_tof0, activation_tof1,delta, min_ts, I,O, entrate_act,uscite_act)
	print("------- RILEVAZIONI ----------")
	print("Entrate ",entrate,"\nUscite ", uscite)

	plt.figure(1, figsize=(15,8))

	plt.plot(lista_ingressi, [10]*len(lista_ingressi), 'ro', color='plum', label='GT entries')

	plt.plot(lista_uscite, [10]*len(lista_uscite), 'ro', color='green', label='GT exits')

	plt.plot(entrate_act, [100]*len(entrate_act), 'ro', color='blue', label='algorithm entries')

	plt.plot(uscite_act, [100]*len(uscite_act), 'ro', color='black', label='algorithm exits')

	plt.plot(uniform_tof1, color='orange', label='Lato 1')

	plt.plot(uniform_tof0, color='red', label='Lato 0')

	#plt.legend(handles=[green_tof,red_tof,alg_entries,alg_exits,true_exits,true_entries])
	plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

	plt.show();



	return entrate, uscite, len(lista_ingressi), len(lista_uscite)
