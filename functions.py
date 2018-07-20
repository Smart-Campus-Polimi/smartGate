import numpy as np
import json
import copy
import datetime
import sys
import getopt

PACKET_LOSS = 30496000;


'''
function to decide which sensor to analize based on input parameters
'''
def parse_args():
	try:
		print(sys.argv[1:])
		opts, args = getopt.getopt(sys.argv[1:], "ip", ["infra=", "pir="])
	except getopt.GetoptError as e:
		print(e)
		sys.exit(0)

	i = False
	p = False


	for o,a in opts:
		if o == "-i":
			i = True
			print("infra enabled")
		elif o == "-p":
			p = True
			print("pir enabled")
		else:
			assert False, "unhandled option"

	return [i,p]


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
processing of the infrareds waveform
'''
def processing_infrared(infrared, enough_zero):
	index_list = [];
	for i in range(0,len(infrared)):
		count = 0;
		if infrared[i][1] == 1:
			for j in range(1, len(infrared)-i):
				if infrared[i+j][1] == 0:
					count = count +1;
					if count > enough_zero:
						index_list.append(infrared[i+j][0])
				else:
					break;

	for i in infrared:
		if i[0] in index_list:
			i[1] = 1
		else:
			i[1] = 0

	return infrared

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
		if dat[i-1] == 0 and dat[i] == 1:
			act.append(i)
		elif dat[i-1] == 1 and dat[i] == 0:
			act.append(i)
	#print ('INIZIO\n')
	#for i in range(0, len(act)-1, 2):
	#	print (act[i+1] - act[i])

	return list(act)

'''
build a list with all the 0-1 fronts
'''
def activate_infra(dat):
	act = [];
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

'''
uniformizza le liste avendo un fondo scala comune
'''
def uniform_list(support, samples_list, min_ts_side, max_ts_side,global_min_ts,global_max_ts):

	lista = copy.deepcopy(support)
    #print(len(samples_list))

    #print("How much zeros at the start: ", min_ts-min_ts_side)
	if min_ts_side > global_min_ts:
		for m in range (0,min_ts_side-global_min_ts):
			lista[m] = 0
	sum_samples = 0
    #print("###",min_ts_side-min_ts)
	for i in range(0,len(samples_list)-1):
        #print (i)
		samples = int(samples_list[i+1][0])-int(samples_list[i][0])
        #mean = (int(samples_list[i][1])+int(samples_list[i+1][1]))/2
        #print(mean)
		for j in range (sum_samples,sum_samples+samples):
			try:
				lista[j+min_ts_side-global_min_ts]=(int(samples_list[i][1]))
			except IndexError:
				print (j+min_ts_side-global_min_ts, "len lista >>> ",len(lista))
				print("i, sample list: ", i, len(samples_list))
				print("!!!samples:    ", samples_list)
				print("The error is: ", index_error)
				print("Happened at time: ",datetime.datetime.now().strftime("%Y-%d-%m %H:%M:%S"))
				return False
		sum_samples = sum_samples + samples
    #print(i,"sum_sample",sum_samples,len(lista),"##",sum_samples-samples,"##",samples)
    #print ("########",i)
    #print("How much zeros at the end: ", max_ts-max_ts_side)
	if max_ts_side < global_max_ts:
		for k in range (max_ts_side,global_max_ts-max_ts_side):
			lista[k]=0
    #print (len(lista))
	return list(lista)

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
							ins = ins + 1;

					elif 'B' == side:
						if matched_entries(zero_up, one_up, other_side_back, other_side_front, span) == 1:
							#print (">>> !! LATO B: Valori trovati, confermo entrata !!\n")
							ins = ins + 1;

				elif zero_up < one_up:
					#print(">>> Sto uscendo\n")

					if 'A' == side:
						if matched_entries(one_up, zero_up, other_side_front, other_side_back, span) == 1:
							#print (">>> !! LATO A: Valori trovati, confermo uscita !!\n")
							out = out + 1;

					elif 'B' == side:
						if matched_entries(one_up, zero_up, other_side_front, other_side_back, span) == 1:
							#print (">>> !! LATO B: Valori trovati, confermo uscita !!\n")
							out = out + 1;


	print ('Side: ', side,' In: ', ins,' Out: ', out);
	return ins, out

'''
count entries for infrared sensors
'''
def count_infrared(activate_infra_0, activate_infra_1, delta):
	I=0
	O=0
	for i in activate_infra_1:
		for j in activate_infra_0:
			if j-i > 0 and j-i < delta:
				I = I+1
			if i-j > 0 and i-j < delta:
				O = O+1

	print ('Infrared:\tIn: ', I,' Out: ', O);

	return I,O


def signal_handler(signal, frame):
	print("\n>>> Exit!")
	sys.exit(0)


''' BETA VERSION
controlla la presenza/assenza di un possibile trenino di persone

def check_train (begin, end, infra_0, infra_1, infrared_param):
	count = 0
	for j in infra_1:
		if (j>begin and j<end):
			count = count + 1
	for k in infra_0:
		if (k>begin and k<end):
			count = count + 1
	#print(count)
	if count > infrared_param:
		print(">>> Trenino")
	else:
		print(">>> No trenino")
	if round((count-2)/2) > 0:
		return round((count-2)/2)
	else:
		return 0
'''