
import jp_graph_trial_tof as jp
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
REAL_OUT = 4
actual_values = [REAL_IN, REAL_OUT]


ground_truth_date = "10_09"
ground_truth_time = "12_58"

#PATH = "/home/cluster/smartGate/"
#PATH = "/home/daniubo/Scrivania/smartGate/"
PATH = "/Users/wunagana/Documents/GitHub/smartGate/"
#DATA_INPUT_A = PATH + "ground_truth_realistic/side_a_"+ground_truth_date+"_part6.json"
#DATA_INPUT_B = PATH + "ground_truth_realistic/side_b_"+ground_truth_date+"_part6.json"
DATA_INPUT_0 = PATH + "ground_truth_realistic/"+ ground_truth_date +"/tof0_"+ground_truth_time+".json"
DATA_INPUT_1 = PATH + "ground_truth_realistic/"+ ground_truth_date +"/tof1_"+ground_truth_time+".json"

results = []

with open(DATA_INPUT_0) as side_a:
	a = json.load(side_a)
with open(DATA_INPUT_1) as side_b:
	b = json.load(side_b)

en = 0
ex = 0



en, ex = jp.just_processing(a, b, ground_truth_time)
