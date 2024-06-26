import argparse
import os
import shutil
import subprocess
import logging
from jinja2 import Environment, FileSystemLoader
from infra.scripts.flow.lib import *
from infra.scripts.flow.publish import *


class Test_lib(Publish):
    def __init__(self,args,publish_src,publish_out,flow_config,local_only_run=0):
        super().__init__(args,publish_src,publish_out,flow_config,local_only_run)
        self.c_test_dict=[]
        self.uvm_test_dict=[]
        self.all_test_dict=[]
    def start(self,):
        if self.local_only_run==1:
            self.local_run()
        else:
            self.refresh_tc()
    def local_run(self):
        # 1 if args.test_case in the dict
        self.refresh_tc()
        logging.info(f"local test begin")
        logging.info(f"we have defined c_test_list: {self.get_test_list(self.c_test_dict)}")
        logging.info(f"we have defined uvm_test_list: {self.get_test_list(self.uvm_test_dict)}")

        for test in self.args.test_case:
            logging.info(f"get test option : {self.get_test_attribute(test,'test_name')}")
            logging.info(f"get test option : {self.get_test_attribute(test,'father_test_name')}")
            logging.info(f"get test option : {self.get_test_attribute(test,'test_type')}")
            logging.info(f"get test option : {self.get_test_attribute(test,'tb_name')}")
            logging.info(f"get test option : {self.get_test_attribute(test,'test_file')}")
            logging.info(f"get test option : {self.get_test_attribute(test,'regression_tag')}")
    def refresh_tc(self):
        self.c_test_list = self.refresh_test_dict(self.publish_out,"_c_test_list.yaml","risc_v_c_test_lib")
        self.uvm_test_list = self.refresh_test_dict(self.publish_out,"_uvm_test_list.yaml","risc_v_uvm_test_lib")
        self.all_test_list.extend(self.c_test_list)
        self.all_test_list.extend(self.uvm_test_list)

    def refresh_test_dict(self,publish_out,suffix,target_tset_lib):
        '''
        output a new test dict that child test has father's attribute
        '''
        test_dict=self.get_test_dict(self.get_test_file(publish_out,suffix),target_tset_lib)
        base_test_share_dict=self.get_test_dict(self.get_test_file(self.publish_out,"_base_test_share.yaml"),"risc_v_base_test_share")
        test_dict.extend(base_test_share_dict)
        return self.inherit_properties(test_dict)

    def get_test_file(self,publish_out_path,suffix):
        '''
        output yaml path
        '''
        for root, dirs, files in os.walk(publish_out_path):
            for file in files:
                if file.endswith(suffix): 
                    logging.info("find test file:{}".format(file))
                    return os.path.join(root, file)
                else:
                    continue
    def get_test_dict(self,yaml_file,test_lib_name):
        '''
        out put test list and attributs
        '''
        yaml_data=read_yaml(yaml_file)
        logging.info(" original test dict :{}".format(yaml_data[test_lib_name]))
        return yaml_data[test_lib_name]

    def get_test_list(self,test_dict):
        '''
        output a list which only have test_name
        '''
        logging.info(f"we got test list {[item['test_name'] for item in test_dict] } in the {test_dict}")
        return [item['test_name'] for item in test_dict]    
    def get_test_attribute(self,test_name,attribute_name):
        for test in self.all_test_dict:  
            if test[str(test_name)] == str(test_name):  
                value = test[str(attribute_name)]  
                logging.info(f"the value of {attribute_name} in {test_name} is {value}")
                return value
            else:   
                logging.error(f"'{test_name}' not found.")  
        return ValueError(f" '{test_name}' not found the attribute {attribute_name} in the cfg file.") 
    def is_test_father(self,test_name,test_dict):
        for item in test_dict:  
            if item['test_name'] == test_name:  
                if item['father_test_name'] in [None, '']:  
                    logging.info(f"{test_name} is father test")
                    return True  
                else:  
                    return False  
        return None     
    def is_test_child(self,test_name,test_dict):
        for item in test_dict:  
            if item['test_name'] == test_name:  
                if item['father_test_name'] is not None and item['father_test_name'] != '':
                    logging.info(f"{test_name} is child test")
                    return True  
                else:  
                    return 0  
        raise ValueError(f"Test name '{test_name}' not found in the test list.") 
    def get_test_command(self,test_name):
        if self.check_tc_exist(test_name):
            return self.get_test_attribute(test_name,'test_option')
        else:
            exit(1)
    def check_tc_exist(self, test_name):
        self.refresh_tc()
        if any(item['test_name'] == test_name for item in self.c_test_dict): 
            c_n=1
            return c_n
        else: 
            c_n=0
        if any(item['father_test_name'] == test_name for item in self.uvm_test_dict):
            u_n=2
            return u_n
        else:
            u_n=0

        return False

    def check_args_tc_exist(self,args):
        self.refresh_tc()
        if len (args.test_case)==0:
            logging.info('test_case is empty')
            if len(args.regr_tag):
                logging.error('test_case and regr_tag are empty, you must define one of it')
                exit(1)
            else:
                logging.info(f'this run is regression , your regression tag is{args.tag}')
        else:
            for test in args.test_case:
                if self.check_tc_exist(test)==1:
                    logging.info(f'{test} is in c_test_list')
                elif self.check_tc_exist(test)==2:
                    logging.info(f'{test} is in uvm_test_list')
                else:
                    logging.error(f'{test} is not in the list')
                    exit(1)
    
    def merge_and_deduplicate(self,d1, d2):  
        """
        合并两个字典，并去重
        """  
        merged = d1.copy()  
        for key, value in d2.items():  
            if key in merged and merged[key] == value:  
                # 如果键存在且值相同，则不合并，避免重复  
                continue  
            merged[key] = value  
        return merged  
    def merge_tags(self,child_tags, father_tags):  
        """
        合并标签，并去重
        """  
        if isinstance(child_tags, str):  
            child_tags = [child_tags]  # 如果是字符串，转化为列表  
        if isinstance(father_tags, str):  
            father_tags = [father_tags]  # 如果是字符串，转化为列表  
        merged_tags = list(set(child_tags + father_tags))  # 合并并去重  
        return merged_tags  
    def inherit_properties(self,tests):  
        """
        遍历tests,继承父类的属性并去重
        """  
        # 创建一个字典，用于快速查找tests  
        test_dict = {test['test_name']: test for test in tests}  
        # 遍历每个test  
        for test in tests:  
            test_name = test['test_name']  
            father_name = test.get('father_test_name', '')  
            
            # 初始化子类的属性  
            child_options = test.get('test_option', {})  
            child_tags = test.get('regression_tag', [])  
            
            # 递归地继承父类的属性  
            while father_name:  
                if father_name not in test_dict:  
                    break  # 如果找不到父类，则停止继承  
                
                father_test = test_dict[father_name]  
                father_options = father_test.get('test_option', {})  
                father_tags = father_test.get('regression_tag', [])  
                
                # 合并并去重test_option  
                child_options = self.merge_and_deduplicate(child_options, father_options)  
                
                # 合并regression_tag  
                child_tags = self.merge_tags(child_tags, father_tags)  
                
                # 继续向上查找祖父类  
                father_name = father_test.get('father_test_name', '')  
            
            # 更新子类的属性  
            test['test_option'] = child_options  
            test['regression_tag'] = child_tags  
        return tests  
    
###########################################################################################
# aims to run publish.py in local, add below main()                                       #
# you must specify 3 arguments: publish_src, publish_out, flow_config                     #
# example: python publish.py -source ./src -out ./publish -config_list ./project.cfg      #
###########################################################################################
                    
def parse_args():
    parser = argparse.ArgumentParser(description="get_test_list script")
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
    Test_lib = Test_lib(args.publish_src,args.publish_out,args.flow_config,local_only_run)
    Test_lib.start()

if __name__ == "__main__":
    main()
