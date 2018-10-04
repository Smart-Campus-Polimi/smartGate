import json
from functions import parse_args
import jp_graph_trial as jp
import jp_graph_trial_tof as jp_tof

import sys
import getopt

use = parse_args()
PIR = use[1]
INFRA = use[0]

DATE = "27_09"
PATH = "/home/daniubo/Scrivania/Git/smartGate/"
TIME = "10_29"
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
if INFRA:
	print("--------------- INF EXECUTION ---------------\n")
	opt_enough_zero = 5
	opt_delta = 800
	jp.just_processing(a, b, opt_delta, opt_enough_zero, use, TIME)
	print("---------------------------------------------\n")

# TOF ANALYSIS
print("--------------- TOF EXECUTION ---------------\n")
en, ex, real_en, real_ex = jp_tof.just_processing(a, b, TIME)
print("---------------------------------------------\n")





