#!/usr/bin/python3
import configparser
import os
import argparse
import logging
from jinja2 import Template, FileSystemLoader, Environment
from infra.scripts.flow.lib import *
from infra.scripts.flow.publish import *

def env_setup(branch_cwd,simulation_path):
    try:
        os.environ["RISCV_DV_ROOT"] = branch_cwd
        logging.info("RISCV_DV_ROOT: " + os.environ["RISCV_DV_ROOT"])
        if os.path.exists(simulation_path):
            os.environ["RISCV_DV_SIM_ROOT"] = simulation_path
            logging.info("RISCV_DV_SIM_ROOT: " + os.environ["RISCV_DV_SIM_ROOT"])
            os.environ["RISCV_DV_PUBLISH_OUT"] = os.path.join(os.environ["RISCV_DV_SIM_ROOT"], "publish")
            logging.info("RISCV_DV_PUBLISH_OUT: " + os.environ["RISCV_DV_PUBLISH_OUT"]) 
    except KeyboardInterrupt:
        logging.info("\n Exited Ctrl-C from user request")
        cwd = os.getcwd()
    except Exception as e:
        logging.info("Exception: " + str(e))
    
    return [os.environ["RISCV_DV_ROOT"] , os.environ["RISCV_DV_SIM_ROOT"] , os.environ["RISCV_DV_PUBLISH_OUT"]]
    
# get directory path
def get_dir_path():
    try:
        cwd = os.path.dirname(os.path.realpath(__file__))
        os.environ["RISCV_DV_ROOT"] = cwd
        print (os.environ["RISCV_DV_ROOT"])
    except KeyboardInterrupt:
        logging.info("\n Exited Ctrl-C from user request")
        cwd = os.getcwd()
    return cwd
# parse args
def parse_args():
    parser = argparse.ArgumentParser(description="DV Runner")
    parser.add_argument('-target',"--target", type=str, default="base_tb", action="store",help="different module target",required=False)
    parser.add_argument('-sim_dir','--sim_dir', type=str, default="./simulation/",action="store", help="simulation file path",required=True)
    # parser.add_argument("-regr_dir", "--regr_dir",type=str, default="./simulation/", help="regression file path")
    parser.add_argument("-log_verbose", "--log_verbose",default=False,action="store_true", help="log verbose",required=False)
    parser.add_argument("-debug", "--debug", type=int,default=0,action="store", help="dump waveform or not ",required=False)
    parser.add_argument("-testcase", "--testcase", type=str,action="append", help="specify testcase",nargs='+',required=True)
    parser.add_argument("-seed", "--seed", type=int,default=100,action="store", help="specify seed",required=False)
    parser.add_argument('--h', action='help', help='Show this help message and exit.')
    args=parser.parse_args()
    # print(args)
    # arg_dict = vars(args)
    # for key, value in arg_dict.items():
    #     print(f"{key}: {value}")

    return args 


# generate test_lib_all
def generate_test_lib_all(config_list):
    env = Environment(loader=FileSystemLoader(os.environ["RISCV_DV_ROOT"]))
    template = env.get_template("test_lib_all.sv")
    output = template.render(config_list)  
def load_config(cfg_path):
    cfg=configparser.ConfigParser()
    cfg.read(cfg_path)
    config_list=[]
    for section in cfg.sections():
        for key in cfg[section]:
            config_list.append((key,cfg[section][key]))
    return [{k:v} for k,v in dict(config_list).items()]


def _get_test_lib_list(self):
    #1. get yaml file path and name who define test_lib
    #2. get test_lib name
    #3. return test_lib list
    pass
def main():
# get directory path
    cwd=get_dir_path()
    args=parse_args()
    setup_logging(args.log_verbose)
    env_setup(cwd,args.sim_dir)
    
    logging.info(vars(args))

    publish = Publish(os.path.join(os.environ["RISCV_DV_ROOT"],'src'),os.environ["RISCV_DV_PUBLISH_OUT"],os.path.join(os.environ["RISCV_DV_ROOT"],'project.cfg'))
    publish.start()

    
if __name__ == "__main__":
    main()

