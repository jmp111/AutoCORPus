import os
import argparse
import re
from utils import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('-f','--filepath',type=str, help="filepath for base HTML document")
    parser.add_argument('-t','--target_dir',type=str, help="target directory")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--config", type=str, help="filepath for configuration JSON file")
    group.add_argument("-d", "--config_dir", type=str, help="directory of configuration JSON files")

    args = parser.parse_args()
    file = args.filepath
    target_dir = args.target_dir
    config = args.config
    config_dir = args.config_dir

    if config_dir:
        config_list = os.listdir(config_dir)
        for config in config_list:
            config = os.path.join(config_dir,config)
            # extract table
            target_path = os.path.join(target_dir,'tables',os.path.basename(config).strip('.json'))
            command = "python ./extract_table.py -f '{}' -t '{}' -c '{}'".format(file,target_path,config)
            os.system(command)

            # extract maintext
            target_path = os.path.join(target_dir,'maintext',os.path.basename(config).strip('.json'))
            command = "python ./extract_maintext.py -f '{}' -t '{}' -c '{}'".format(file,target_path,config)
            os.system(command)

            # extract abbreviations
            maintext_json_path = os.path.join(target_dir, 'maintext', os.path.basename(file).strip('.html') + '_maintext.json')
            target_path = os.path.join(target_dir,'abbreviations',os.path.basename(config).strip('.json'))
            command = "python ./extract_abbreviations.py -f '{}' -t '{}' ".format(maintext_json_path,target_path)
            os.system(command)
    else:
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