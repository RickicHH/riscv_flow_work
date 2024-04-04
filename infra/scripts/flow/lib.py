import os
import random
import sys
import re
import subprocess
import time
import yaml
import logging

RETURN_SUCCESS = 0
RETURN_FAIL    = 1
RETURN_FATAL   = -1

def setup_logging(verbose):
    """
    control print information in the flow log 

    Args:
      verbose: Verbose logging
    """
    if verbose:
        logging.basicConfig(
            format="%(asctime)s %(filename)s:%(lineno)-5s %(levelname)-8s %(message)s",
            datefmt='%a, %d %b %Y %H:%M:%S',
            level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s",
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            level=logging.INFO)


def read_yaml(yaml_file):
    """ 
    Read YAML file to a dictionary

    Args:
      yaml_file : YAML file

    Returns:
      yaml_data : data read from YAML in dictionary format
    """
    with open(yaml_file, "r") as f:
        try:
            yaml_data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            logging.error(exc)
            sys.exit(RETURN_FAIL)
    return yaml_data

def get_project_config(yaml_file):
    with open (yaml_file, 'r') as f:
        vars =yaml.safe_load(f.read())
    return vars
