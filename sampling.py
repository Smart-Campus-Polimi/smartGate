import json
import glob

SAMPLING = 6
DATE = "/09_10"

PATH = "/users/wunagana/Documents/GitHub/smartGate/ground_truth_realistic"+DATE
OUTPUT_JSON = PATH+"_sampling/multiple_tof_"+DATE.replace("/", "")
files=(glob.glob(PATH+"/*.json"))
files.sort()
for sampling_file in files:
    TIME = str(sampling_file[85:90])
    #print(sampling_file)
    with open(sampling_file) as SF:
        a = json.load(SF)
        for i in range(0,len(a)):
            '''
            print("------ "+TIME+" ------------ "+str(i)+" --------------------------------------------")
            print (a[i]['TOF0'])
            print (a[i]['TOF1'])
            '''
            a[i]['TOF0'] = a[i]['TOF0'][0::SAMPLING]
            a[i]['TOF1'] = a[i]['TOF1'][0::SAMPLING]
            '''
            print("############")
            print (a[i]['TOF0'])
            print (a[i]['TOF1'])
            print("------------------------------------------------------------------------------------")
            '''
    OUTPUT = str(OUTPUT_JSON+"_ore_"+TIME+"_SAMPLING_passo"+str(SAMPLING)+".json")
        #print(OUTPUT)

    with open(OUTPUT, "w") as outfile:
        json.dump(a,outfile)
