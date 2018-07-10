import numpy as np
import json
import copy
import datetime

PACKET_LOSS = 30496000;

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
	time_vect = np.arange(start_time, end_time, interval)
	return time_vect.tolist()


'''
processing of the infrareds waveform
'''
def processing_infrared(infrared):
	index_list = [];
	for i in range(0,len(infrared)):
		count = 0;
		if infrared[i][1] == '1':
			for j in range(1, len(infrared)-i):
				if infrared[i+j][1] == '0':
					count = count +1;
					if count > 10:
						index_list.append(infrared[i+j][0])
				else:
					break;

	for i in infrared:
		if i[0] in index_list:
			i[1] = "1"
		else:
			i[1] = "0"

	return infrared

'''
Function to detect matched entries between the two side of the gate.
'''
def matched_entries(ts_in, ts_out, other_side_in, other_side_out):
	flag_first_side = 0;	# flag che determina la presenza di un valore idoneo per il primo pir dell'altro lato
	flag_second_side = 0;	# flag che determina la presenza di un valore idoneo per il secondo pir dell'altro lato
	for ts in other_side_in:
		'''
		controllo che sia presente sul lato opposto un valore di timestamp
		nell'intorno della salita del pir verso il lato d'ingresso
		'''
		if ts_in + 900 > ts and ts_in - 900 < ts:
			flag_first_side = 1;

	for ts in other_side_out:
		'''
		controllo che sia presente sul lato opposto un valore di timestamp
		nell'intorno della salita del pir verso il lato d'uscita
		'''
		if ts_out + 900 > ts and ts_out - 900 < ts:
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
controlla la presenza/assenza di un possibile trenino di persone
'''
def check_train (begin, end, infra_0, infra_1):
	count = 0
	for j in infra_1:
		if (j>begin and j<end):
			count = count + 1
	for k in infra_0:
		if (k>begin and k<end):
			count = count + 1
	print(count)
	if count > 4:
		print(">>> Trenino")
	else:
		print(">>> No trenino")
	if round((count-2)/2) > 0:
		return round((count-2)/2)
	else:
		return 0

'''
Detect entries based on the difference of the changes of value
of the PIRs.
Computed for each side of the gate.
'''
def count_entries(front, back, side, other_side_front, other_side_back, infra_0, infra_1):
	if 'A' == side:
		print ("###########################\n>>> VERIFICA LATO A\n###########################\n")
	if 'B' == side:
		print ("###########################\n>>> VERIFICA LATO B\n###########################\n")
	ins = 0
	out = 0

	for i in range(0, len(front)-1, 2):
		for j in range(0, len(back)-1, 2):
			#print ('Ingresso esaminato: ', front[i])
			#print ('Uscita esaminata: ', back[j])
			if abs(front[i] - back[j]) < 1600:
				#print ('La differenza è inferiore a 1600 ms')
				zero_up = back[j]
				zero_down = back[j+1]
				one_up = front[i]
				one_down = front[i+1]

				if zero_up > one_up:
					errors = check_train(one_up,zero_down,infra_0,infra_1)
					print (">>> Sto entrando\n")
					'''
					Confronto i valori dei due sensori sullo stesso lato con l'intorno degli stessi sull'altro lato
					del gate per cercare un valore simile dei PIR del lato opposto
					'''
					if 'A' == side:
						if matched_entries(zero_up, one_up, other_side_back, other_side_front) == 1:
							print (">>> !! LATO A: Valori trovati, confermo entrata !!\n")
							if errors != 0:
								print(errors," ingressi in più")
							ins = ins + 1 + errors;

					elif 'B' == side:
						if matched_entries(zero_up, one_up, other_side_back, other_side_front) == 1:
							print (">>> !! LATO B: Valori trovati, confermo entrata !!\n")
							if errors != 0:
								print(errors," ingressi in più")
							ins = ins + 1 + errors;

				elif zero_up < one_up:

					errors = check_train(zero_up,one_down,infra_0,infra_1)

					print(">>> Sto uscendo\n")

					if 'A' == side:
						if matched_entries(one_up, zero_up, other_side_front, other_side_back) == 1:
							print (">>> !! LATO A: Valori trovati, confermo uscita !!\n")
							if errors != 0:
								print(errors," uscite in più")
							out = out + 1 + errors;

					elif 'B' == side:
						if matched_entries(one_up, zero_up, other_side_front, other_side_back) == 1:
							print (">>> !! LATO B: Valori trovati, confermo uscita !!\n")
							if errors != 0:
								print(errors," uscite in più")
							out = out + 1 + errors;


	print ('Side: ', side,' In: ', ins,' Out: ', out);
	return ins, out
