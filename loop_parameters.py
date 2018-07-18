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

REAL_IN = 23
REAL_OUT = 23
actual_values = [REAL_IN, REAL_OUT]
span = [600, 700, 800, 850,900]
infrared_param = [4, 5, 7, 10, 12]
enough_zero = [10, 15, 20, 25, 30]
delta = [1000, 1200, 1400, 1600, 1800]
delta_jump = 200

ground_truth_date = "17_07"

PATH = "/home/cluster/smartGate/"
DATA_INPUT_A = PATH + "ground_truth/side_a_"+ground_truth_date+".json"
DATA_INPUT_B = PATH + "ground_truth/side_b_"+ground_truth_date+".json"
OUTPUT_PATH = PATH+"output/"+ground_truth_date+'results.csv'
OUTPUT_PATH_PARTIAL = PATH+"output/"+ground_truth_date+'partial.csv'

results = []


use = parse_args()



with open(DATA_INPUT_A) as side_a:
	a = json.load(side_a)
with open(DATA_INPUT_B) as side_b:
	b = json.load(side_b)

en = 0
ex = 0
for s in span:
#for s in range(span[0], span[-1], 50):
	for d in range(delta[0], delta[-1], delta_jump):
		en, ex = jp.just_processing(a, b, d, s, None, None, use)
		temp = [] 
		temp.append(en)
		temp.append(ex)
		pred = [en, ex]
		temp.append("%.2f" % sqrt(mean_squared_error(actual_values, pred)))
		temp.append("%.2f" % mean_absolute_error(actual_values, pred))
		temp.append(s)
		temp.append(d)
		results.append(temp)
		with open(OUTPUT_PATH_PARTIAL, 'a') as partial:
			writer = csv.writer(partial, delimiter=';')
			writer.writerow(temp) 
		

results_pd = pd.DataFrame(results, columns=['IN', 'OUT', 'RMSE', 'MAE', 'span', 'delta'])
#print(results_pd)
results_pd.to_csv(OUTPUT_PATH, sep='\t')

