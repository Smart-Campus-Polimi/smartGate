import pandas as pd
import csv

M_TO_S = 60
S_TO_MS = 1000
H_TO_M = 60

INPUT_FILE = "/home/daniubo/Scrivania/smartGate/appTS/ts_30_07.txt"
OUTPUT_FILE = "/home/daniubo/Scrivania/smartGate/appTS/ts_csv.csv"

with open(INPUT_FILE, "r") as f:
	lines_list = []
	table = []
	for line in f:
		verso = line[0]
		temp = []
		if verso == 'I':
			temp.append(1)
			temp.append(0)
		else:
			temp.append(0)
			temp.append(1)	
		milliseconds = int(line[15:17])*H_TO_M*M_TO_S*S_TO_MS + int(line[18:20])*M_TO_S*S_TO_MS + int(line[21:23])*S_TO_MS
		print(line[15:17]+":"+line[18:20]+":"+line[21:23]+"\t"+str(milliseconds))
		temp.append(milliseconds)
		table.append(temp)

pandas_table = pd.DataFrame(table, columns=['in', 'out', 'time'])
pandas_table.to_csv(OUTPUT_FILE, sep='\t')