# HOW TO USE
# Inserire la data. Utilizzato per creare csv in cui sono scritti ingressi/uscite dei TOF per 
# orari distribuiti sulle 24h. 
# Necessitano -t -d nella riga di comando per attivare l'analisi dei tof doppi sullo stesso mkr.

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

DATE = "16_10"
PATH = "/home/daniubo/Scrivania/Git/smartGate/"
#PATH = "/Users/wunagana/Documents/GitHub/smartGate/"
#PATH = "/home/cluster/smartGate/"
#DATA_INPUT_A = PATH + "ground_truth_realistic/"+ DATE + "/side_a_" + TIME + ".json"
#DATA_INPUT_B = PATH + "ground_truth_realistic/"+ DATE + "/side_b_" + TIME + ".json"
OUTPUT_PATH = PATH+"/analysis/graph_analysis/flux_estimation/"
files = list(glob.glob(os.path.join(PATH + 'ground_truth_realistic/'+DATE+'/' , '*.*')))
files.sort()
#for f in files:
#	print(f)


results = []
for f in files:
	with open(f) as side_a:
		a = json.load(side_a)
	# TOF ANALYSIS
	print("--------------- TOF EXECUTION ---------------\n")
	#per gli indici di Dani
	h = f[80:82]
	m = f[83:85]
	TIME = f[80:85]
	#per gli indici del cluster
	#h = f[66:68]
	#m = f[69:71]
	#TIME = f[66:71]
	#indici andre (con sampling)
	#h = f[104:106]
	#m = f[107:109]
	#TIME = f[104:109]
	print("Execution @"+h+":"+m)
	try:
		en, ex, real_en, real_ex = jp.just_processing(a, a, 0, 0, use, TIME)
		print("---------------------------------------------\n")
		
	except TypeError:
		print("--------------------------------------------")
		print("----------------- ERROR --------------------")
		print("------- Pass to the next 5 minutes ---------")
	results = []
	results.append([h+":"+m, real_en, en, real_ex, ex])
	with open(OUTPUT_PATH+DATE+"_all_flux.csv", 'a') as partial:
		writer = csv.writer(partial, delimiter=';')
		writer.writerow(results)
