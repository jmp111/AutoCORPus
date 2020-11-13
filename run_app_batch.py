import os
import argparse
import re
from utils import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('-b','--base_dir',type=str)
    parser.add_argument('-t','--target_dir',type=str)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--config", type=str, help="filepath for configuration JSON file")
    group.add_argument("-d", "--config_dir", type=str, help="directory of configuration JSON files")
    # parser.add_argument('-a','--associated_data',type=str, help="directory of associated data")

    args = parser.parse_args()
    base_dir = args.base_dir
    target_dir = args.target_dir
    config = args.config
    config_dir = args.config_dir
    # associated_data = args.associated_data

    filelist = get_files(base_dir)
    
    if config_dir:
        config_list = os.listdir(config_dir)
        for config in config_list:
            config = os.path.join(config_dir,config)
            for file in filelist:
                # extract table
                target_path = os.path.join(target_dir,'tables',os.path.basename(config).strip('.json'))
                command = "python ./extract_table.py -f " + file + " -t " + target_path + " -c " + config
                os.system(command)

                # extract maintext
                target_path = os.path.join(target_dir,'maintext',os.path.basename(config).strip('.json'))
                command = "python ./extract_maintext.py -f " + file + " -t " + target_path + " -c " + config
                os.system(command)

                # extract abbreviations
                maintext_json_path = os.path.join(target_dir, 'maintext', os.path.basename(file).strip('.html') + '_maintext.json')
                target_path = os.path.join(target_dir,'abbreviations',os.path.basename(config).strip('.json'))
                command = "python ./extract_abbreviations.py -f " + maintext_json_path + " -t " + target_path
                os.system(command)
    else:
        for file in filelist:
            # extract table
            command = "python ./extract_table.py -f " + file + " -t " + os.path.join(target_dir,'tables') + " -c " + config
            os.system(command)

            # extract maintext
            command = "python ./extract_maintext.py -f " + file + " -t " + os.path.join(target_dir,'maintext') + " -c " + config
            os.system(command)

            maintext_json_path = os.path.join(target_dir, 'maintext', os.path.basename(file).strip('.html') + '_maintext.json')
            # extract abbreviations
            command = "python ./extract_abbreviations.py -f " + maintext_json_path + " -t " + os.path.join(target_dir,'abbreviations')
            os.system(command)