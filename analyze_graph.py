import json
from functions import parse_args
import jp_graph_trial as jp

import sys
import getopt

use = parse_args()
PIR = use[1]
INFRA = use[0]
TOF = use[5]

DATE = "27_09"
PATH = "/home/daniubo/Scrivania/Git/smartGate/"
#PATH = "/Users/wunagana/Documents/GitHub/smartGate/"
TIME = "10_14"
DATA_INPUT_A = PATH + "ground_truth_realistic/"+ DATE + "/side_a_" + TIME + ".json"
DATA_INPUT_B = PATH + "ground_truth_realistic/"+ DATE + "/side_b_" + TIME + ".json"

with open(DATA_INPUT_A) as side_a:
	a = json.load(side_a)
with open(DATA_INPUT_B) as side_b:
	b = json.load(side_b)

if PIR:
	print("--------------- PIR EXECUTION ---------------\n")
	opt_span = 900
	opt_delta = 1000
	jp.just_processing(a, b, opt_delta, opt_span, use, TIME)
	print("---------------------------------------------\n")

if TOF and INFRA:
	# MATCHING ANALYSIS
	opt_enough_zero = 3
	opt_delta = 850
	print("--------------- MATCH EXECUTION ---------------\n")
	en, ex, real_en, real_ex = jp.just_processing(a, b, opt_delta, opt_enough_zero, use, TIME)
	print("---------------------------------------------\n")

elif INFRA:
	print("--------------- INF EXECUTION ---------------\n")
	opt_enough_zero = 3
	opt_delta = 850
	jp.just_processing(a, b, opt_delta, opt_enough_zero, use, TIME)
	print("---------------------------------------------\n")

elif TOF:
	# TOF ANALYSIS
	print("--------------- TOF EXECUTION ---------------\n")
	en, ex, real_en, real_ex = jp.just_processing(a, b, 0, 0, use, TIME)
	print("---------------------------------------------\n")


