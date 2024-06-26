import argparse
import os
import shutil
import subprocess
import logging
from jinja2 import Environment, FileSystemLoader
from infra.scripts.flow.lib import *

class Publish(object):
    def __init__(self,args,publish_src,publish_out,flow_config,local_only_run=0):
        self.args = args
        self.publish_src = publish_src
        self.publish_out = publish_out
        self.flow_config = flow_config
        self.local_only_run = local_only_run
        
    def start(self):
        if(self.local_only_run):
            logging.info("local publish start")
            self._copy_file(self.publish_src,self.publish_out)
            logging.info("local publish done")
            logging.info("local publish translate start")
            config_list=get_project_config(self.flow_config)
            self._translate_j2(self.publish_out,config_list)
            logging.info("local publish translate done")
        else :
        # 1. move all files to publish folder include DV and DE file 
            logging.info("publish start")
            src = os.path.join(self.publish_src,'src/rtl')
            dst = os.path.join(self.publish_out,'rtl')
            self._copy_file(src,dst)
            logging.info("publish rtl done")
            logging.info("publish verify start")
            src = os.path.join(self.publish_src,'src/verify')
            dst = os.path.join(self.publish_out,'verify')
            self._copy_file(src,dst)
            logging.info("publish verify done")
        # 2. translate .j2 
            logging.info("publish load config start")
            config_list=get_project_config(self.flow_config)
            logging.info("publish load config done")
            logging.info("publish translate start")
            self._translate_j2(os.path.join(self.publish_out,'rtl'),config_list)
            self._translate_j2(os.path.join(self.publish_out,'verify'),config_list)
            logging.info("publish translate done")

        
    def _copy_file(self,src,dst):
        for root, dirs, files in os.walk(src):
            for file in files:
                if file.endswith('.v' or '.sv' or '.j2' or '.yaml' or '.c'): 
                    src_file = os.path.join(root, file)  
                    dst_file = os.path.join(dst, file)  
                    shutil.copy(src_file, dst_file)  
                    logging.info(f"copy {src_file} to {dst_file}")
        
    def get_publish_file_name(self,file_name):
        return os.path.join(self.publish_out,file_name)
    
    def get_publish_file_path(self,file_path):
        return os.path.join(self.publish_out,file_path)
    
    
    def _translate_j2(self,path,config_list):
        # 1. translate .j2 to .sv
        # 2. and rename then rm the .j2 file
        env = Environment(loader=FileSystemLoader('.'))
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.j2'):
                    template = env.get_template(file)
                    output = template.render(config_list)
                    with open(os.path.join(root, file)[:-3] , 'w') as f:
                        f.write(output)
                    logging.info(f'translate {file} to {file[:-3]}')
                    subprocess.run(f"rm {os.path.join(root, file)}", shell=True, check=True)



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
    publish = Publish(args,args.publish_src,args.publish_out,args.flow_config,local_only_run)
    publish.start()

if __name__ == "__main__":
    main()
