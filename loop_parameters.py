# HOW TO USE
# Inserire le opportune date e orari e da terminale attivare le opzioni per i sensori 
# che si desiderare analizzare. Questo programma è per l'analisi di PIR e TOF. 
# Necessario inserire i parametri per l'analisi.
import jp_graph_trial as jp
from functions import parse_args
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from math import sqrt
import json
import pandas as pd
import time
import csv
import sys
import getopt

import functions as f

ground_truth_date = "27_09"
ground_truth_time = "12_02"



DATA = "27-09-2018"
PATH_GT = "GT_telefono/"+ground_truth_date+"/"
DATE =  "27_09.txt"
#PATH = "/home/cluster/smartGate/"
PATH = "/home/daniubo/Scrivania/Git/smartGate/"
#PATH = "/Users/wunagana/Documents/GitHub/smartGate/"
#DATA_INPUT_A = PATH + "ground_truth_realistic/side_a_"+ground_truth_date+"_part6.json"
#DATA_INPUT_B = PATH + "ground_truth_realistic/side_b_"+ground_truth_date+"_part6.json"
DATA_INPUT_A = PATH + "ground_truth_realistic/"+ ground_truth_date +"/side_a_"+ground_truth_time+".json"
DATA_INPUT_B = PATH + "ground_truth_realistic/"+ ground_truth_date +"/side_b_"+ground_truth_time+".json"



results = []


use = parse_args()
PIR = use[1]
INFRA = use[0]

if PIR == True:
	var = [800,1000]
	delta = [900,1100]
	var_jump = 50
	delta_jump =  50
	OUTPUT_PATH = PATH+"output/"+ground_truth_date+"/pir/"+ground_truth_time+"_pir_results.csv"
	OUTPUT_PATH_PARTIAL = PATH+"output/"+ground_truth_date+"/pir/"+ground_truth_time+"_pir_partials.csv"

elif INFRA == True:
	#enough_zero = var?
	var = [3, 7]
	delta = [800, 1150]
	var_jump = 1
	delta_jump = 50
	OUTPUT_PATH = PATH+"output/"+ground_truth_date+"/inf/"+ground_truth_time+"_inf_results.csv"
	OUTPUT_PATH_PARTIAL = PATH+"output/"+ground_truth_date+"/inf/"+ground_truth_time+"_inf_partials.csv"


with open(DATA_INPUT_A) as side_a:
	a = json.load(side_a)
with open(DATA_INPUT_B) as side_b:
	b = json.load(side_b)

en = 0
ex = 0

for d in range(delta[0], delta[1]+delta_jump, delta_jump):
	for v in range(var[0], var[1]+var_jump, var_jump):
		en, ex, min_ts, max_ts = jp.just_processing(a, b, d, v, use, ground_truth_time)
		temp = []
		REAL_IN, REAL_OUT = f.get_ground_truth(PATH_GT, DATE, DATA, min_ts, max_ts)
		actual_values = [len(REAL_IN), len(REAL_OUT)]
		temp.append(len(REAL_IN))
		temp.append(en)
		temp.append(len(REAL_OUT))
		temp.append(ex)
		pred = [en, ex]
		temp.append("%.2f" % sqrt(mean_squared_error(actual_values, pred)))
		temp.append("%.2f" % mean_absolute_error(actual_values, pred))
		if actual_values[0] != 0 and actual_values[1] != 0:
			acc_in = 100-(abs(en-actual_values[0])/actual_values[0] * 100)
			acc_out = 100-(abs(ex-actual_values[1])/actual_values[1] * 100)
			temp.append(acc_in)
			temp.append(acc_out)
		else:
			temp.append('NaN')
			temp.append('NaN')
		temp.append(v)
		temp.append(d)
		results.append(temp)
		with open(OUTPUT_PATH_PARTIAL, 'a') as partial:
			writer = csv.writer(partial, delimiter=';')
			writer.writerow(temp)


if INFRA:
	results_pd = pd.DataFrame(results, columns=['REAL IN', 'IN', 'REAL OUT', 'OUT', 'RMSE', 'MAE', 'ACC. IN', 'ACC.OUT', 'enough_zero', 'delta'])
	print("Ho finito :)")
	results_pd.to_csv(OUTPUT_PATH, sep='\t')
elif PIR:
	results_pd = pd.DataFrame(results, columns=['REAL IN', 'IN', 'REAL OUT', 'OUT', 'RMSE', 'MAE', 'ACC. IN', 'ACC.OUT', 'span', 'delta'])
	print("Ho finito :)")
	results_pd.to_csv(OUTPUT_PATH, sep='\t')
