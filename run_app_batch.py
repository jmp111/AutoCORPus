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

    args = parser.parse_args()
    base_dir = args.base_dir
    target_dir = args.target_dir
    config = args.config
    config_dir = args.config_dir

    filelist = get_files(base_dir)
    
    if config_dir:
        config_list = os.listdir(config_dir)
        for config in config_list:
            config = os.path.join(config_dir,config)
            for file in filelist:
                # extract table
                command = "python ./extract_table.py -f '{}' -t '{}' -c '{}'".format(file,os.path.join(target_dir,'tables_'+config.strip('.json')),config)
                os.system(command)

                # extract maintext
                command = "python ./extract_maintext.py -f '{}' -t '{}' -c '{}'".format(file,os.path.join(target_dir,'maintext_'),config)
                os.system(command)

                maintext_json_path = os.path.join(target_dir, 'maintext', os.path.basename(file).strip('.html') + '_maintext.json')
                # extract abbreviations
                command = "python ./extract_abbreviations.py -f '{}' -t '{}' ".format(maintext_json_path,os.path.join(target_dir,'abbreviations_'+config.strip('.json')))
                os.system(command)
    else:
        for file in filelist:
            # extract table
            command = "python ./extract_table.py -f '{}' -t '{}' -c '{}'".format(file,os.path.join(target_dir,'tables'),config)
            os.system(command)

            # extract maintext
            command = "python ./extract_maintext.py -f '{}' -t '{}' -c '{}'".format(file,os.path.join(target_dir,'maintext'),config)
            os.system(command)

            maintext_json_path = os.path.join(target_dir, 'maintext', os.path.basename(file).strip('.html') + '_maintext.json')
            # extract abbreviations
            command = "python ./extract_abbreviations.py -f '{}' -t '{}' ".format(maintext_json_path,os.path.join(target_dir,'abbreviations'))
            os.system(command)