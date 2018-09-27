import json
import glob
from jsonmerge import merge

result = []
output_list = []
DATE = "/27_09"
LATO = "a" #scegliere se unire il lato a o b
PATH = "/users/wunagana/Documents/GitHub/smartGate/ground_truth_realistic"+DATE
OUTPUT_JSON = PATH+"/side_"+LATO+"_"+DATE.replace("/", "")+".json"
files=(glob.glob(PATH+"/side_"+LATO+"*.json"))


def cat_json(output_filename, input_filenames):

    final_file = "["
    for infile_name in input_filenames:
        with open(infile_name) as infile:
            data = infile.read()
            data = data[1:-1]
            final_file = final_file + data + ","

    final_file = final_file[:-1]
    final_file = final_file + "]"
    with open(output_filename, "w") as outfile:
        outfile.write(final_file)

files.sort()

print(files)
cat_json(OUTPUT_JSON,files)
