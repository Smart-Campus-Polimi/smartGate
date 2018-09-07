import pandas as pd
import csv

M_TO_S = 60
S_TO_MS = 1000
H_TO_M = 60

TIME = "16_42"
INPUT_FILE = "/home/daniubo/Scrivania/smartGate/appTS/TS_"+TIME+".txt"
OUTPUT_FILE = "/home/daniubo/Scrivania/smartGate/appTS/ts_"+TIME+"_csv.csv"

with open(INPUT_FILE, "r") as f:
	lines_list = []
	table = []
	for line in f:
		verso = line[0]
		temp = []
		milliseconds = (int(line[15:17])-1)*H_TO_M*M_TO_S*S_TO_MS + int(line[18:20])*M_TO_S*S_TO_MS + int(line[21:23])*S_TO_MS
		print(line[15:17]+":"+line[18:20]+":"+line[21:23]+"\t"+str(milliseconds))
		temp.append(milliseconds)
		if verso == 'I':
			temp.append(1)
			temp.append(0)
		else:
			temp.append(0)
			temp.append(1)
		table.append(temp)

pandas_table = pd.DataFrame(table, columns=['time', 'in', 'out'])
pandas_table.to_csv(OUTPUT_FILE, sep='\t')