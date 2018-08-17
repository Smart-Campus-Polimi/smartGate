import json
from functions import parse_args
import just_processing as jp
import sys
import getopt

use = parse_args()
PIR = use[1]
INFRA = use[0]

PATH = "/home/daniubo/Scrivania/smartGate/"
TIME = "15_57"
DATA_INPUT_A = PATH + "ground_truth_realistic/" + "side_a_" + TIME + ".json"
DATA_INPUT_B = PATH + "ground_truth_realistic/" + "side_b_" + TIME + ".json"

with open(DATA_INPUT_A) as side_a:
	a = json.load(side_a)
with open(DATA_INPUT_B) as side_b:
	b = json.load(side_b)

if PIR:
	opt_span = 850
	opt_delta = 1200
	jp.just_processing(a, b, opt_delta, opt_span, use)

if INFRA:
	opt_enough_zero = 26
	opt_delta = 1200
	jp.just_processing(a, b, opt_delta, opt_enough_zero, use)




