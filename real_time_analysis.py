import os
import signal
import datetime
import glob
import jp_graph_trial as jp
import functions as f
from functions import parse_args
import schedule
import json
import paho.mqtt.client as mqtt

PATH = "/home/daniubo/Scrivania/Git/smartGate/"
#PATH = "/Users/wunagana/Documents/GitHub/smartGate/"
BROKER_ADDRESS = "10.79.1.176"
TOPIC = "smartGate/sg1/mls/flux"
CLIENT_NAME = "localhost_kagedani"
client = mqtt.Client(CLIENT_NAME)
client.loop_start()
client.connect(BROKER_ADDRESS)

def make_sure_path_exists(path):
	if not os.path.exists(path):
		os.makedirs(path)

def analysis():
	print(">>> Analyzing")
	DATE = str(datetime.datetime.now().strftime('%d_%m')) 
	make_sure_path_exists(PATH+"ground_truth_realistic/"+DATE)
	make_sure_path_exists(PATH+"ground_truth_realistic/"+DATE+"_analyzed")
	files=(glob.glob(PATH+"ground_truth_realistic/"+DATE+"/*.json"))
	if len(files) == 0:
		print("No files in the directory. Program ended.")
		return 1
	elif len(files) == 1:
		#print("File analizzato: ", files)
		with open(files[0]) as side_a:
			a = json.load(side_a)
		h = files[0][80:82]
		m = files[0][83:85]
		TIME = files[0][80:85]
		#indici andre
		#h = files[0][84:86]
		#m = files[0][87:89]
		#TIME = files[0][84:89]
		print("Execution @"+h+":"+m)
		try:
			en, ex, real_en, real_ex = jp.just_processing(a, a, 0, 0, use, TIME)
			data = {
					"in" : str(ex),
					"out": str(en)
			}
			data_j = json.dumps(data)
			client.publish(TOPIC, data_j, qos=1)
		except TypeError:
			print("--------------------------------------------")
			print("----------------- ERROR --------------------")
			print("------- Pass to the next 5 minutes ---------")
		os.rename(PATH+"ground_truth_realistic/"+DATE+"/"+files[0][67:], PATH+"ground_truth_realistic/"+DATE+"_analyzed/"+files[0][67:])
		return 1

def main():
	schedule.every(1).minutes.do(analysis);

	while True:
		schedule.run_pending()


if __name__ == '__main__':
	signal.signal(signal.SIGINT, f.signal_handler)
	use = parse_args()
	main()