'''
>>> 17-07
i = 23
o = 23

>>> 19-07
- ora: 14
i = 21 (+/-2)
o = 17 (+/-2)
'''

import just_processing as jp
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

REAL_IN = 17
REAL_OUT = 13
actual_values = [REAL_IN, REAL_OUT]


ground_truth_date = "23_07"

PATH = "/home/cluster/smartGate/"
DATA_INPUT_A = PATH + "ground_truth/side_a_1h_"+ground_truth_date+".json"
DATA_INPUT_B = PATH + "ground_truth/side_b_1h_"+ground_truth_date+".json"
OUTPUT_PATH = PATH+"output/"+ground_truth_date+'_1h_pir_results.csv'
OUTPUT_PATH_PARTIAL = PATH+"output/"+ground_truth_date+'_1h_pir_partial.csv'

results = []


use = parse_args()
PIR = use[1]
INFRA = use[0]

if PIR == True:
	var = [600,1000]
	delta = [1400, 2000]
	var_jump = 50
	delta_jump = 100

elif INFRA == True:
	#enough_zero = var?
	var = [15, 25]
	delta = [1400, 2000]
	var_jump = 1
	delta_jump = 100


with open(DATA_INPUT_A) as side_a:
	a = json.load(side_a)
with open(DATA_INPUT_B) as side_b:
	b = json.load(side_b)

en = 0
ex = 0


for d in range(delta[0], delta[1]+delta_jump, delta_jump):
	for v in range(var[0], var[1]+var_jump, var_jump):
		en, ex = jp.just_processing(a, b, d, v, use)
		temp = [] 
		temp.append(en)
		temp.append(ex)
		pred = [en, ex]
		temp.append("%.2f" % sqrt(mean_squared_error(actual_values, pred)))
		temp.append("%.2f" % mean_absolute_error(actual_values, pred))
		temp.append(v)
		temp.append(d)
		results.append(temp)
		with open(OUTPUT_PATH_PARTIAL, 'a') as partial:
			writer = csv.writer(partial, delimiter=';')
			writer.writerow(temp) 
		

if INFRA:
	results_pd = pd.DataFrame(results, columns=['IN', 'OUT', 'RMSE', 'MAE', 'enough_zero', 'delta'])
	print("Ho finito :)")
	results_pd.to_csv(OUTPUT_PATH, sep='\t')
elif PIR:
	results_pd = pd.DataFrame(results, columns=['IN', 'OUT', 'RMSE', 'MAE', 'span', 'delta'])
	print("Ho finito :)")
	results_pd.to_csv(OUTPUT_PATH, sep='\t')