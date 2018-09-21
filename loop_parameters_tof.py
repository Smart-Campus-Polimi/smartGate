
import jp_graph_trial_tof as jp
from functions import parse_args
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from math import sqrt
import json
import pandas as pd
import time
import csv
from pathlib import Path

ground_truth_date = "21_09"
ground_truth_time = "09_55"

output_date = "21_09"


#PATH = "/home/cluster/smartGate/"
#PATH = "/home/daniubo/Scrivania/smartGate/"
PATH = "/Users/wunagana/Documents/GitHub/smartGate/"
#DATA_INPUT_A = PATH + "ground_truth_realistic/side_a_"+ground_truth_date+"_part6.json"
#DATA_INPUT_B = PATH + "ground_truth_realistic/side_b_"+ground_truth_date+"_part6.json"
DATA_INPUT_0 = PATH + "ground_truth_realistic/"+ ground_truth_date +"/side_a_"+ground_truth_time+".json"
DATA_INPUT_1 = PATH + "ground_truth_realistic/"+ ground_truth_date +"/side_b_"+ground_truth_time+".json"

results = []

with open(DATA_INPUT_0) as side_a:
	a = json.load(side_a)
with open(DATA_INPUT_1) as side_b:
	b = json.load(side_b)

en = 0
ex = 0



en, ex, real_en, real_ex = jp.just_processing(a, b, ground_truth_time)

actual_values = [real_en, real_ex]
temp = []
temp.append(ground_truth_time)
temp.append(real_en)
temp.append(en)
temp.append(real_ex)
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

results.append(temp)
OUTPUT_PATH = PATH+"output/"+output_date+"/"+output_date+"_tof_results.csv"
file = Path(OUTPUT_PATH)
if file.is_file():
	with open(OUTPUT_PATH, 'a') as partial:
		writer = csv.writer(partial, delimiter=';')
		writer.writerow(results)
else:
	results_pd = pd.DataFrame(results, columns=['TIME', 'REAL IN', 'IN', 'REAL OUT', 'OUT', 'RMSE', 'MAE', 'ACC. IN', 'ACC.OUT'])
	print("Ho finito :)")
	results_pd.to_csv(OUTPUT_PATH, sep='\t')
