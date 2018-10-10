# HOW TO USE
# Inserire la data. Utilizzato per creare csv in cui sono scritti ingressi/uscite dei TOF per 
# orari distribuiti sulle 24h. 
# Necessitano -t -s nella riga di comando per attivare l'analisi dei tof divisi su due mkr.


import json
from functions import parse_args
import jp_graph_trial as jp

import sys
import getopt
import csv
import os
import glob

use = parse_args()
TOF = use[5]

DATE = "27_09"
PATH = "/home/daniubo/Scrivania/Git/smartGate/"
#PATH = "/Users/wunagana/Documents/GitHub/smartGate/"
#DATA_INPUT_A = PATH + "ground_truth_realistic/"+ DATE + "/side_a_" + TIME + ".json"
#DATA_INPUT_B = PATH + "ground_truth_realistic/"+ DATE + "/side_b_" + TIME + ".json"
OUTPUT_PATH = PATH+"/analysis/graph_analysis/flux_estimation/"
files_a = list(glob.glob(os.path.join(PATH + 'ground_truth_realistic/'+DATE+'/' , 'side_a*.*')))
files_b = list(glob.glob(os.path.join(PATH + 'ground_truth_realistic/'+DATE+'/' , 'side_b*.*')))
files_a.sort()
files_b.sort()


for f in range(0, len(files_a)):
	with open(files_a[f]) as side_a:
		a = json.load(side_a)
	with open(files_b[f]) as side_b:
		b = json.load(side_b)
	# TOF ANALYSIS
	print("--------------- TOF EXECUTION ---------------\n")
	h = files_a[f][74:76]
	m = files_a[f][77:79]
	TIME = files_a[f][74:79]
	print("Execution @"+TIME)
	en, ex, real_en, real_ex = jp.just_processing(a, b, 0, 0, use, TIME)
	print("---------------------------------------------\n")
	results = []
	results.append([h+":"+m, en, ex])
	'''
	with open(OUTPUT_PATH+DATE+"_all_flux.csv", 'a') as partial:
			writer = csv.writer(partial, delimiter=';')
			writer.writerow(results)
	'''