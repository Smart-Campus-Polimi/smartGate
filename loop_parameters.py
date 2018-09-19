'''
>>> 17-07
i = 23
o = 23

>>> 19-07
- ora: 14
i = 21 (+/-2)
o = 17 (+/-2)

>>> 23-07
i = 17
o = 13

>>> 24-07
i = 17			i = 9		i = 11		i = 8
o = 18			o = 14		o = 10		o = 9
SECONDO NON PULITO

>>> 26-07
i = 5			i = 12		i = 12		i = 9+sedia		i = 4		i = 18	
o = 5			o = 10		o = 10		o = 10			o = 7		o = 17
'''

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

REAL_IN = 4
REAL_OUT = 0
actual_values = [REAL_IN, REAL_OUT]


ground_truth_date = "13_09"
ground_truth_time = "15_33"

#PATH = "/home/cluster/smartGate/"
PATH = "/home/daniubo/Scrivania/smartGate/"
#PATH = "/Users/wunagana/Documents/GitHub/smartGate/"
#DATA_INPUT_A = PATH + "ground_truth_realistic/side_a_"+ground_truth_date+"_part6.json"
#DATA_INPUT_B = PATH + "ground_truth_realistic/side_b_"+ground_truth_date+"_part6.json"
DATA_INPUT_A = PATH + "ground_truth_realistic/"+ ground_truth_date +"/sensors/side_a_"+ground_truth_time+".json"
DATA_INPUT_B = PATH + "ground_truth_realistic/"+ ground_truth_date +"/sensors/side_b_"+ground_truth_time+".json"



results = []


use = parse_args()
PIR = use[1]
INFRA = use[0]

if PIR == True:
	var = [600,1000]
	delta = [800, 1900]
	var_jump = 50
	delta_jump =  50
	OUTPUT_PATH = PATH+"output/"+ground_truth_date+"/"+ground_truth_time+"_pir_results.csv"
	OUTPUT_PATH_PARTIAL = PATH+"output/"+ground_truth_date+"/"+ground_truth_time+"_pir_partials.csv"

elif INFRA == True:
	#enough_zero = var?
	var = [15,30]
	delta = [1000, 1900]
	var_jump = 1
	delta_jump = 50
	OUTPUT_PATH = PATH+"output/"+ground_truth_date+"/"+ground_truth_time+"_inf_results.csv"
	OUTPUT_PATH_PARTIAL = PATH+"output/"+ground_truth_date+"/"+ground_truth_time+"_inf_partials.csv"


with open(DATA_INPUT_A) as side_a:
	a = json.load(side_a)
with open(DATA_INPUT_B) as side_b:
	b = json.load(side_b)

en = 0
ex = 0

for d in range(delta[0], delta[1]+delta_jump, delta_jump):
	for v in range(var[0], var[1]+var_jump, var_jump):
		en, ex = jp.just_processing(a, b, d, v, use, ground_truth_time)
		temp = []
		temp.append(REAL_IN)
		temp.append(en)
		temp.append(REAL_OUT)
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
