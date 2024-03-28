import argparse
import os
import shutil
import subprocess
import logging
from jinja2 import Environment, FileSystemLoader
from infra.scripts.flow.lib import *
from infra.scripts.flow.publish import *


class Test_lib(Publish):
    def __init__(self):
        super().__init__(self)

    def run(self):

        pass

    def get_c_test_file(self,publish_out_path):
        for root, dirs, files in os.walk(publish_out_path):
            for file in files:
                if file.endswith('_c_test_list.yaml'): 
                    return os.path.join(root, file)
                else:
                    continue
    def get_uvm_test_file(self,publish_out_path):
        for root, dirs, files in os.walk(publish_out_path):
            for file in files:
                if file.endswith('_uvm_test_list.yaml'): 
                    return os.path.join(root, file)
                else:
                    continue
    def get_test_dict(self,yaml_file,test_lib_name):
        yaml_data=read_yaml(yaml_file)
        return yaml_data[test_lib_name]
    def get_test_attribute(self,test_name,attribute_name,test_dict):
        for test in test_dict:  
            if test['test_name'] == str(test_name):  
                value = test[str(attribute_name)]  
                break  
            else:   
                print("Test with name 'hello_world' not found.")  
                value = None  
        return value
    

    def is_test_father(self,test_name):
        pass
    
    def is_test_child(self,test_name):
        pass

    def get_father_test_cfg(self,father_test_name):
        pass

    def get_child_test_cfg(self,child_test_name):
        pass

    def merger_fater_test_cfg(self,father_test_name,child_test_name):
        pass

    def get_child_test_cfg(self,child_test_name):
        pass

    def publish_share_command(self):
        pass

    def publish_each_test_command(self):
        pass

    def test_is_child(self,test_name):
        pass
    def test_is_parent(self,test_name):
        pass

###########################################################################################
# aims to run publish.py in local, add below main()                                       #
# you must specify 3 arguments: publish_src, publish_out, flow_config                     #
# example: python publish.py -source ./src -out ./publish -config_list ./project.cfg      #
###########################################################################################
                    
def parse_args():
    parser = argparse.ArgumentParser(description="DV Runner")
    parser.add_argument('-source',"--publish_src", type=str, default="no", action="store",help="define a source path",required=False)
    parser.add_argument('-out','--publish_out', type=str, default="no",action="store", help="define a final path",required=False)
    parser.add_argument('-config_list','--flow_config', type=str, default="no",action="store", help="define a flow config file",required=False)
    parser.add_argument("-log_verbose", "--log_verbose",default=False,action="store_true", help="log verbose",required=False)
    parser.add_argument('--h', action='help', help='Show this help message and exit.')
    args=parser.parse_args()
    return args 

def main():
    local_only_run=1
    args=parse_args()
    setup_logging(args.log_verbose)
    publish = Publish(args.publish_src,args.publish_out,args.flow_config,local_only_run)
    publish.start()

if __name__ == "__main__":
    main()
