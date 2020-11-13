# AutoSCOPyST


## Getting Started

### Single File
`$FILEPATH` indicates the PubMed HTML file that will be processed
`$TARGET_DIR` indicates the target directory for the output JSON files
`$CONFIG` indicates the configuration file 

    python run_app.py -f $FILEPATH -t $TARGET_DIR -c $CONFIG

If associated data is available, use `$ASSOCIATED_DATA` to indicate the directory that contains associated data, and use `-a` or `--associated_data` command

    python run_app.py -f $FILEPATH -t $TARGET_DIR -c $CONFIG -a $ASSOCIATED_DATA


If multiple configuration files are used, use `$CONFIG_DIR` for the directory of configuration files, and use

    python run_app.py -f $FILEPATH -t $TARGET_DIR -d $CONFIG_DIR

### Multiple Files
`$BASE_DIR` indicates the PubMed HTML file that will be processed
`$TARGET_DIR` indicates the target directory for the output JSON files
`$CONFIG` indicates the configuration file 

    python run_app_batch.py -b $BASE_DIR -t $TARGET_DIR -c $CONFIG

If multiple configuration files are used, use `$CONFIG_DIR` for the directory of configuration files, and use

    python run_app_batch.py -b $BASE_DIR -t $TARGET_DIR -d $CONFIG_DIR

### Configurations

Configuration files are needed to adjust for many different formats from publishers and websites. If the configuration files provided result in missing information, create a new configuration file that works.

- Open the HTML document in any browser and use inspection tool (you can do this with text editor but insepection tool is easier)
- Find the corresponding element in the HTML script
- Find the unique HTML tag and class attribute for the element