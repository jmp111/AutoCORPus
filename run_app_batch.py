import os
import argparse
import re
from utils import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('-b', '--base_dir', type=str)
    parser.add_argument('-t', '--target_dir', type=str)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--config", type=str, help="filepath for configuration JSON file")
    group.add_argument("-d", "--config_dir", type=str, help="directory of configuration JSON files")
    parser.add_argument('-a', '--associated_data', type=bool,
                        help="True if associated data is available, folder needs to be in the same directory with the base html file and has the same name")

    args = parser.parse_args()
    base_dir = args.base_dir
    target_dir = args.target_dir
    config = args.config
    config_dir = args.config_dir
    associated_data = args.associated_data

    filelist = get_files(base_dir)

    if config_dir:
        config_list = os.listdir(config_dir)
        for config in config_list:
            config = os.path.join(config_dir, config)
            for file in filelist:
                # extract table
                target_path = os.path.join(target_dir, 'tables', os.path.basename(config).replace('.json', ''))
                command = "python ./extract_table.py -f \"" + file + "\" -t \"" + target_path + "\" -c \"" + config + "\""
                os.system(command)

                # extract table images
                image = os.path.join(file, 'image')
                if os.path.isdir(image):
                    target_path = os.path.join(target_dir, 'table_image', os.path.basename(config).replace('.json', ''))
                    command = "python ./extract_table_image.py -f \"" + image + "\" -t \"" + target_path + "\" -c \"" + config + "\""
                    os.system(command)

                # extract maintext
                target_path = os.path.join(target_dir, 'maintext', os.path.basename(config).replace('.json', ''))
                command = "python ./extract_maintext.py -f \"" + file + "\" -t \"" + target_path + "\" -c \"" + config + "\""
                os.system(command)

                # extract abbreviations
                maintext_json_path = os.path.join(target_dir, 'maintext',
                                                  os.path.basename(file).replace('.html', '') + '_maintext.json')
                target_path = os.path.join(target_dir, 'abbreviations', os.path.basename(config).replace('.json', ''))
                command = "python ./extract_abbreviations.py -f \"" + maintext_json_path + "\" -t \"" + target_path + "\""
                os.system(command)


    else:
        for file in filelist:
            # extract table
            command = "python ./extract_table.py -f \"" + file + "\" -t \"" + os.path.join(target_dir,
                                                                                     'tables') + "\" -c \"" + config + "\""
            os.system(command)

            # extract table images
            image = os.path.join(file, 'image')
            if os.path.isdir(image):
                command = "python ./extract_table_image.py -f \"" + image + "\" -t \"" + os.path.join(target_dir,
                                                                                     'table_image') + "\" -c \"" + config + "\""
                os.system(command)

            # extract maintext
            command = "python ./extract_maintext.py -f \"" + file + "\" -t \"" + os.path.join(target_dir,
                                                                                     'maintext') + "\" -c \"" + config + "\""
            os.system(command)

            maintext_json_path = os.path.join(target_dir, 'maintext',
                                              os.path.basename(file).replace('.html', '') + '_maintext.json')
            # extract abbreviations
            command = "python ./extract_abbreviations.py -f \"" + file + "\" -t \"" + os.path.join(target_dir,
                                                                                     'abbreviations') + "\""
            os.system(command)

    if associated_data:
        for file in filelist:
            # extract associated data
            associated_data_dir = os.path.join(base_dir,
                                               os.path.basename(file).replace('.html', '') + '_associated_data')
            if os.path.isdir(associated_data_dir):
                command = "python ./extract_associated_data.py -a \"" + associated_data_dir + "\" -t \"" + os.path.join(
                    target_dir, 'associated_data') + "\""
            os.system(command)
