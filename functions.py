import numpy as np
import json
import copy
import datetime
import sys
import getopt

PACKET_LOSS = 8190;


'''
function to decide which sensor to analize based on input parameters
'''
def parse_args():
	try:
		print(sys.argv[1:])
		opts, args = getopt.getopt(sys.argv[1:], "ipcgmtsda", ["infra=", "pir=", "camera=", "graph=", "match=", "tof=", "single=", 'double=', 'arduino='])
	except getopt.GetoptError as e:
		print(e)
		sys.exit(0)

	i = False
	p = False
	c = False
	g = False
	m = False
	t = False
	s = False
	d = False
	a = False

	for o,a in opts:
		if o == "-i":
			i = True
			print("infra enabled")
		elif o == "-p":
			p = True
			print("pir enabled")
		elif o == "-c":
			c = True
			print("camera enabled")
		elif o == "-g":
			g = True
			print("graph enabled")
		elif o == "-m":
			m = True
			print("match enabled")
		elif o == "-t":
			t = True
			print("tof enabled")
		elif o == "-s":
			s = True
			print("single tof enabled")
		elif o == "-d":
			d = True
			print("double tof enabled")
		elif o == "-a":
			a = True
			print("arduino enabled")
		else:
			assert False, "unhandled option"

	return [i,p,c,g,m,t,s,d,a]


'''
function that removes the errors in the timestamps due to missed packets from ntp server
'''
def correcting_errors(data):
	for i in range(len(data)):
		time = int(data[i]['Time'])
		if time == PACKET_LOSS:
			for j in range(0,len(data[i:])):
				if(int(data[i+j]['Time'])) != PACKET_LOSS:
					data[i]['Time'] = int(data[i+j]['Time'])-j*1000;
					break;
'''
function that removes the errors in the timestamps due to missed packets from ntp server
'''
def correcting_errors_tof(data):
	count_how_many_consecutive_oor = 0
	count_how_many_oor = 0
	for i in range(0,len(data)):
		distance = data[i][1]
		if i == len(data)-1:
			data[i][1] = data[i-1][1]
		elif distance > 1300:
			#print("Data[i]: ",data[i],"\tData[i+1]: ", data[i+1])
			data[i][1] = 1200

	return list(data)

'''
Create  list with all the time interval equispaced
'''
def building_time(data, interval):
	end_time = int(data['Time'])
	start_time = end_time - 1000
	try:
		#print(interval)
		time_vect = []
		time_vect = np.arange(start_time, end_time, interval)
	except ZeroDivisionError as e:
		print(e)
		print ("Start: ", start_time)
		print ("End: ", end_time)
		print ("Interval: ", interval)
	return list(time_vect)

'''
BETA VERSION: alternative way to build a list of activation for infrared samples
'''
def processing_infrared_2(infrared, enough_zero):
	index_list = []
	len_infra = len(infrared)-1
	for i in range(0,len(infrared)):
		count = 0
		j = 0
		if infrared[i][1] == 1 and i+1<len_infra:
			j = i
			while infrared[j+1][1] == 0:
				count += 1
				if j+1<len_infra:
					j += 1
				else:
					break
			if count > enough_zero:
				index_list.append(infrared[i][0])
			else:
				j_final = j
				j = j - count - 1
				while j<j_final:
					infrared[j][1] = 0
					j = j + 1
	#print("Lista:", index_list)
	return list(index_list), infrared


'''
Function to detect matched entries between the two side of the gate.
'''
def matched_entries(ts_in, ts_out, other_side_in, other_side_out, span):
	flag_first_side = 0;	# flag che determina la presenza di un valore idoneo per il primo pir dell'altro lato
	flag_second_side = 0;	# flag che determina la presenza di un valore idoneo per il secondo pir dell'altro lato
	for ts in other_side_in:
		'''
		controllo che sia presente sul lato opposto un valore di timestamp
		nell'intorno della salita del pir verso il lato d'ingresso
		'''
		if ts_in + span > ts and ts_in - span < ts:
			flag_first_side = 1;

	for ts in other_side_out:
		'''
		controllo che sia presente sul lato opposto un valore di timestamp
		nell'intorno della salita del pir verso il lato d'uscita
		'''
		if ts_out + span > ts and ts_out - span < ts:
			flag_second_side = 1;

	'''
	Se è presente almeno uno dei due valori allora ho verificato la condizione di 3 pir su 4
	'''
	return (flag_first_side or flag_second_side);

'''
Detect the activation of PIRs verifyng how many
steps are in their magnitude envelope
'''
def activate(dat):
	act = [];

	for i in range(1, len(dat)):
		if dat[i-1][1] == 0 and dat[i][1] == 1:
			act.append((dat[i-1][0]+dat[i][0])/2)
		elif dat[i-1][1] == 1 and dat[i][1] == 0:
			act.append((dat[i-1][0]+dat[i][0])/2)
	return list(act)

'''
da aggiungere il fronte di discesa per il controllo tra i due fronti in modo
tale da eliminare nel conteggio delle attivazioni eventi che durano meno di
un passaggio normale
'''

def activate_tof(dat):
	act = [];
	deact = [];
	lista_elim = [];
	min_mov = 40
	for i in range(1, len(dat)):
		if dat[i-1] == 1200 and dat[i] != 1200:
			act.append(i)
		if dat[i-1] != 1200 and dat[i]== 1200:
			deact.append(i)
	#print ("act ",len(act))
	for j in range (0,len(deact)-1):
		if deact[j]-act[j] < min_mov:
			lista_elim.append(act[j])
	for x in lista_elim:
		#print( x)
		act.remove(x)
	return list(act)

'''
build a list with all the 0-1 fronts
'''
def activate_infra(dat):
	act = [];
	print(dat)
	for i in range(1, len(dat)):
		if dat[i-1] == 0 and dat[i] == 1:
			act.append(i)
	return list(act)

'''
converte caratteri nelle liste in interi
'''
def convert_list_int(list):
    for i in range (0,len(list)):
        list[i][1]=int(list[i][1]);
    return list



def uniform_list_tof(support, samples_list, min_ts_side, max_ts_side,global_min_ts,global_max_ts):

	lista = copy.deepcopy(support)
	#print(len(lista))
	#print("sample_list:",len(samples_list))
	#print("How much zeros at the start: ", global_min_ts-min_ts_side)
	#print("How much zeros at the end: ", global_max_ts-max_ts_side)
	if min_ts_side > global_min_ts:
		for m in range (0,min_ts_side-global_min_ts):
			lista[m] = 1200
	sum_samples = 0
	#print("###",min_ts_side-global_min_ts)
	for i in range(0,len(samples_list)-1):
		#print(i,"###",sum_samples)
		samples = int(samples_list[i+1][0])-int(samples_list[i][0])
        #mean = (int(samples_list[i][1])+int(samples_list[i+1][1]))/2
        #print(mean)
		for j in range (sum_samples,sum_samples+samples):
			try:
				lista[j+min_ts_side-global_min_ts]=(int(samples_list[i][1]))
			except IndexError:
				print (j+min_ts_side-global_min_ts, "len lista >>> ",len(lista))
				print("i, sample list: ", i, len(samples_list))
				#print("!!!samples:    ", samples_list)
				#print("The error is: ", Index_error)
				print("Happened at time: ",datetime.datetime.now().strftime("%Y-%d-%m %H:%M:%S"))
				return False
		sum_samples = sum_samples + samples
	#print("How much zeros at the end: ", global_max_ts-max_ts_side)
	if max_ts_side < global_max_ts:

		for k in range (0,global_max_ts-max_ts_side):
			#print(k)
			lista[len(lista)-k-1]=lista[len(lista)-(global_max_ts-max_ts_side+1)]
	#print (lista)

	for i in range(0,len(lista)):
		'''
		il valore 1300 è il range massimo del sensore mentre 1000 dipende dalla larghezza del gate
		'''
		if lista[i] > 1000 and lista[i] <1300:
			lista[i] = 1200
	return list(lista)

'''
def uniform_list_tof_2(support, samples_list, min_ts_side, max_ts_side,global_min_ts,global_max_ts):

	lista = copy.deepcopy(support)
	lista_append = []
	#print(len(lista))
	#print("sample_list:",len(samples_list))
	
	if min_ts_side > global_min_ts:
		for m in range (0,min_ts_side-global_min_ts):
			print("Aggiunto all'inizio,", m)
			lista_append.append(1200)
	sum_samples = 0
	#print("###",min_ts_side-global_min_ts)
	for s in range(0, len(samples_list)-1):
		for i in range(samples_list[s][0], samples_list[s+1][0]):
			lista_append.append(int(samples_list[s][1]))

	#print("How much zeros at the end: ", global_max_ts-max_ts_side)
	if max_ts_side < global_max_ts:
		for k in range (0,global_max_ts-max_ts_side):
			print("Aggiunto alla fine,", k)
			lista_append.append(1200)
	#print (lista)

	for i in range(0,len(lista_append)):
		if lista_append[i] > 1000 and lista_append[i] <1300:
			lista_append[i] = 1200
	#print(lista_append)
	print(len(lista), len(lista_append))
	print("differenza:", len(lista_append) - len(lista))
	print("How much zeros at the start: ", global_min_ts-min_ts_side)
	print("How much zeros at the end: ", global_max_ts-max_ts_side)
	for r in range(0, len(lista_append) - len(lista)):
		lista_append.pop(0)
	return list(lista_append)
'''
'''
genera maschera per analisi del trenino
'''
def generate_mask (support,list0a,list0b,list1a,list1b):
    mask = copy.deepcopy(support)
    for i in range(0,len(mask)):
        mask[i] = list0a[i] or list0b[i] or list1a[i] or list1b[i]
    return list(mask)

'''
Detect entries based on the difference of the changes of value
of the PIRs.
Computed for each side of the gate.
'''
def count_entries(front, back, side, other_side_front, other_side_back, delta, span):
	'''
	if 'A' == side:
		#print ("\n###########################\n>>> VERIFICA LATO A\n###########################\n")
	if 'B' == side:
		#print ("###########################\n>>> VERIFICA LATO B\n###########################\n")
	'''
	ins = 0
	out = 0
	g_entries_a = []
	g_entries_b = []
	g_exits_a = []
	g_exits_b = []
	for i in range(0, len(front)-1, 2):
		for j in range(0, len(back)-1, 2):
			#print ('Ingresso esaminato: ', front[i])
			#print ('Uscita esaminata: ', back[j])
			if abs(front[i] - back[j]) < delta:
				#print ('La differenza è inferiore a 1600 ms')
				zero_up = back[j]
				zero_down = back[j+1]
				one_up = front[i]
				one_down = front[i+1]

				if zero_up > one_up:
					#print (">>> Sto entrando\n")
					'''
					Confronto i valori dei due sensori sullo stesso lato con l'intorno degli stessi sull'altro lato
					del gate per cercare un valore simile dei PIR del lato opposto
					'''
					if 'A' == side:
						if matched_entries(zero_up, one_up, other_side_back, other_side_front, span) == 1:
							#print (">>> !! LATO A: Valori trovati, confermo entrata !!\n")
							ins = ins + 1
							g_entries_a.append((zero_up+one_up)/2)
					elif 'B' == side:
						if matched_entries(zero_up, one_up, other_side_back, other_side_front, span) == 1:
							#print (">>> !! LATO B: Valori trovati, confermo entrata !!\n")
							ins = ins + 1
							g_entries_b.append((zero_up+one_up)/2)
				elif zero_up < one_up:
					#print(">>> Sto uscendo\n")

					if 'A' == side:
						if matched_entries(one_up, zero_up, other_side_front, other_side_back, span) == 1:
							#print (">>> !! LATO A: Valori trovati, confermo uscita !!\n")
							out = out + 1
							g_exits_a.append((zero_up+one_up)/2)
					elif 'B' == side:
						if matched_entries(one_up, zero_up, other_side_front, other_side_back, span) == 1:
							#print (">>> !! LATO B: Valori trovati, confermo uscita !!\n")
							out = out + 1
							g_exits_b.append((zero_up+one_up)/2)

	print ('Side: ', side,' In: ', ins,' Out: ', out);
	if side == 'A':
		return ins, out, g_entries_a, g_exits_a
	elif side == 'B':
		return ins, out, g_entries_b, g_exits_b


'''
count entries and exit from tof sensor
'''
def count_entries_tof(act_list0, act_list1, delta, I, O, E, U):

	for i in range(0,len(act_list1)):
		for j in range(0,len(act_list0)):

			if act_list1[i]<=act_list0[j] and act_list0[j]-act_list1[i] <= delta:
				E.append(((act_list0[j]+act_list1[i])/2))
				I += 1
				#print("########### Ingresso ###########")
				#print("tof0: "+str(act_list0[j])+"\ttof1: "+str(act_list1[i])+"\n")
				act_list0.pop(j)
				act_list1.pop(i)
				I, O, E, U = count_entries_tof(act_list0, act_list1, delta, I, O, E, U)
				return I, O, E, U;

			elif act_list1[i]>act_list0[j] and act_list1[i]-act_list0[j] <= delta:
				U.append(((act_list0[j]+act_list1[i])/2))
				O += 1
				#print("########### Uscita ###########")
				#print("tof0: "+str(act_list0[j])+"\ttof1: "+str(act_list1[i])+"\n")
				act_list0.pop(j)
				act_list1.pop(i)
				I, O, E, U = count_entries_tof(act_list0, act_list1, delta, I, O, E, U)
				return I, O, E, U;

	return I,O,E,U

'''
Function to retrieve the ground truth of different span in time
'''
def get_ground_truth(path, date, data, min_ts, max_ts):
	lines = [line.rstrip('\n') for line in open(path+date)]
	ingresso = []
	lista_ingressi = []
	uscita = []
	lista_uscite = []
	FUSO_ORARIO = 7198000
	#print (max_ts%86400000+FUSO_ORARIO,"<- max ######### min -> ",min_ts%86400000+FUSO_ORARIO)
	for i in lines:
		if i[0] == "I" and i[4:14] == data:

			millisecondi = sum(int(x) * 60 ** j for j,x in enumerate(reversed(i[16:24].split(":"))))*1000
			#print ("Analisi: ", millisecondi)
			if millisecondi >= (min_ts%86400000 + FUSO_ORARIO) and millisecondi <= ((max_ts%86400000) + FUSO_ORARIO):
				#print("I",millisecondi)
				lista_ingressi.append(millisecondi-(min_ts%86400000 + FUSO_ORARIO))
		elif i[0] == "O" and i[5:15] == data:
			millisecondi = sum(int(x) * 60 ** j for j,x in enumerate(reversed(i[17:25].split(":"))))*1000
			#print ("Analisi: ", millisecondi)
			if millisecondi >= (min_ts%86400000 + FUSO_ORARIO) and millisecondi <= ((max_ts%86400000) + FUSO_ORARIO):
				#print("O",millisecondi)
				lista_uscite.append(millisecondi-(min_ts%86400000 + FUSO_ORARIO))
	print("------- GROUND TRUTH ---------")
	print("Entrate ",len(lista_ingressi))
	print("Uscite ",len(lista_uscite))
	return list(lista_ingressi),list(lista_uscite)

'''
analysis of data derived from arduino's algorithm
- used to compare accuracy of its algorithm and the python one
'''
def get_analysis_from_arduino(path, lights_file, data, min_ts, max_ts):
	lines = [line.rstrip('\n') for line in open(path+lights_file)]
	ingresso = []
	lista_ingressi = []
	uscita = []
	lista_uscite = []
	FUSO_ORARIO = 7198000
	#print (max_ts%86400000+FUSO_ORARIO,"<- max ######### min -> ",min_ts%86400000+FUSO_ORARIO)
	for i in lines:
		if i[22:23] == "I" and i[1:11] == data:
			millisecondi = sum(int(x) * 60 ** j for j,x in enumerate(reversed(i[12:20].split(":"))))*1000
			#print ("Analisi: ", millisecondi)
			if millisecondi >= (min_ts%86400000 + FUSO_ORARIO) and millisecondi <= ((max_ts%86400000) + FUSO_ORARIO):
				#print("I",millisecondi)
				lista_ingressi.append(millisecondi-(min_ts%86400000 + FUSO_ORARIO))
		elif i[22:23] == "U" and i[1:11] == data:
			millisecondi = sum(int(x) * 60 ** j for j,x in enumerate(reversed(i[12:20].split(":"))))*1000
			#print ("Analisi: ", millisecondi)
			if millisecondi >= (min_ts%86400000 + FUSO_ORARIO) and millisecondi <= ((max_ts%86400000) + FUSO_ORARIO):
				#print("O",millisecondi)
				lista_uscite.append(millisecondi-(min_ts%86400000 + FUSO_ORARIO))
	print("------- OUTPUT ARDUINO ---------")
	print("Entrate ",len(lista_uscite))
	print("Uscite ",len(lista_ingressi))
	return list(lista_ingressi),list(lista_uscite)


# convert timestamp from ms to dates for graphs
def from_ms_to_date(data):
	return str(datetime.datetime.fromtimestamp(data//1000.0))[11:]

# function to manage the forced stop of the program
def signal_handler(signal, frame):
	print("\n>>> Exit!")
	sys.exit(0)

# function to update TOF data with INFRA data
def cross_check(TOF, INF, full):
	for t in range(0, len(TOF)):
		for i in range(0, len(INF)):
			if abs(TOF[t][0]-INF[i][0]) <= 300:
				#print("Intervalli considerati:\nTOF: ", TOF[t][0], "\tINF: ", INF[i][0],"\n")
				INF.pop(i)
				TOF.pop(t)
				cross_check(TOF, INF, full)
				return full

	for i in INF:
		#print(">>> Aggiunto infrarosso!\n")
		#print("\tTS:",i[0])
		if i[1] == 1.5:
			#print("Ingresso")
			full.append([i[0], 1])
		elif i[1] == 3.5:
			#print("Uscita")
			full.append([i[0], 3])
	return full.sort()



'''
def count_infrared(activate_infra_0, activate_infra_1, delta, I, O, E, U):
	I=0
	O=0
	graph_entries = []
	graph_exits = []
	found = False
	#print(activate_infra_0)
	#print('##########################')
	#print(activate_infra_1)
	for a1 in activate_infra_1:
		for a0 in activate_infra_0:
			if a0>a1 and a0-a1<delta and not found:
				graph_entries.append((a0+a1)/2)
				I += 1

	for a1 in activate_infra_1:
		for a0 in activate_infra_0:
			if a1>a0 and a1-a0<delta:
				graph_exits.append((a0+a1)/2)
				O += 1
	
	print ('Infrared:\tIn: ', I,' Out: ', O);

	return I, O, graph_entries, graph_exits


#uniformizza le liste avendo un fondo scala comune
def uniform_list(support, samples_list, min_ts_side, max_ts_side,global_min_ts,global_max_ts):

	lista = copy.deepcopy(support)
	#print("Samples list len: ", len(samples_list))

	#print("How much zeros at the start: ", global_min_ts-min_ts_side)
	if min_ts_side > global_min_ts:
		for m in range (0,min_ts_side-global_min_ts):
			lista[m] = 0
	sum_samples = 0
	#print("###",min_ts_side-min_ts)
	for i in range(0,len(samples_list)-1):
		samples = int(samples_list[i+1][0])-int(samples_list[i][0])
		
		#if samples!=10 and samples!=11:
		#	print ("##############################", i)
		#	print("Number of samples to add: ", samples)
		#mean = (int(samples_list[i][1])+int(samples_list[i+1][1]))/2
		#	print("Value to insert in those samples: ", samples_list[i][1])
		
		for j in range (sum_samples,sum_samples+samples):
			try:
				lista[j+min_ts_side-global_min_ts]=(int(samples_list[i][1]))
			except IndexError:
				print (j+min_ts_side-global_min_ts, "len lista >>> ",len(lista))
				print("i, sample list: ", i, len(samples_list))
				print("Sample_list(i)(1): ", samples_list[i][1])
				#print("!!!samples:    ", samples_list)
				#print("The error is: ", Index_error)
				print("Happened at time: ",datetime.datetime.now().strftime("%Y-%d-%m %H:%M:%S"))
				return False
		sum_samples = sum_samples + samples
    #print("How much zeros at the end: ", max_ts-max_ts_side)
	if max_ts_side < global_max_ts:
		for k in range (max_ts_side,global_max_ts-max_ts_side):
			lista[k]=0
    #print (len(lista))
	return list(lista)

'''