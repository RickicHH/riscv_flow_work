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
        # 1 get test_dict
        c_test_file=self.get_test_file(self.publish_out,"_c_test_list.yaml")
        c_test_dict=self.get_test_dict(c_test_file)
        uvm_test_file=self.get_test_file(self.publish_out,"_uvm_test_list.yaml")
        uvm_test_dict=self.get_test_dict(uvm_test_file)
        base_test_share=self.get_test_file(self.publish_out,"_base_test_share.yaml")
        base_test_share_dict=self.get_test_dict(base_test_share)
        # 2 merge test_dict
        c_test_dict.update(base_test_share_dict)
        uvm_test_dict.update(base_test_share_dict)

        # 3 copy and merge father test_option to child test_option
        self.merge_father_details(c_test_dict)
        self.merge_father_details(uvm_test_dict)

        # 4 

    def get_test_file(self,publish_out_path,suffix):
        for root, dirs, files in os.walk(publish_out_path):
            for file in files:
                if file.endswith(suffix): 
                    return os.path.join(root, file)
                else:
                    continue
    
    def get_test_dict(self,yaml_file,test_lib_name):
        yaml_data=read_yaml(yaml_file)
        return yaml_data[test_lib_name]
    def get_test_list(self,test_dict):
        return [item['test_name'] for item in test_dict]  
        
    def get_test_attribute(self,test_name,attribute_name,test_dict):
        for test in test_dict:  
            if test['test_name'] == str(test_name):  
                value = test[str(attribute_name)]  
                break  
            else:   
                print(f"Test with test name '{test_name}' not found.")  
                value = None  
        return value
    

    def is_test_father(self,test_name,test_dict):
        for item in test_dict:  
            if item['test_name'] == test_name:  
                if item['father_test_name'] in [None, '']:  
                    return True  
                else:  
                    return 0  
        return None  
    
    def is_test_child(self,test_name,test_dict):
        for item in test_dict:  
            if item['test_name'] == test_name:  
                if item['father_test_name'] is not None and item['father_test_name'] != '':  
                    return True  
                else:  
                    return 0  
        raise ValueError(f"Test name '{test_name}' not found in the test list.") 

    def get_father_test_attribute(self,father_test_name,attribute_name,test_dict):
        for item in test_dict:  
            if item['test_name'] == father_test_name:  
                return item[attribute_name]  
        return ValueError(f"Fater test name '{father_test_name}' not found in the test list.") 

    def merge_and_deduplicate(self,options):  
        return list(dict.fromkeys(options))  
    
    def merge_father_details(self,test_list):  
        # 递归函数，用于合并父类和子类的信息  
        def merge_recursive(test_item):  
            # 当前测试项的名称  
            current_test_name = test_item['test_name']  
            # 如果存在父类，递归合并父类信息  
            if 'father_test_name' in test_item:  
                father_name = test_item['father_test_name']  
                father_test = next((item for item in test_list if item['test_name'] == father_name), None)  
                if father_test:  
                    # 递归合并父类信息  
                    merge_recursive(father_test)  
                    
                    # 合并选项和标签，并删除重复项  
                    test_item['test_option'] = self.merge_and_deduplicate(test_item['test_option'] + father_test['test_option'])  
                    test_item['regression_tag'] = self.merge_and_deduplicate(test_item['regression_tag'] + father_test['regression_tag'])  
            
            # 移除father_test_name字段  
            test_item.pop('father_test_name', None)  
        
        # 对每个测试项应用递归合并函数  
        for test in test_list:  
            merge_recursive(test)  
        
        # 无需返回新的列表，因为我们在原地修改了test_list  

    def publish_share_command(self):
        pass

    def publish_each_test_command(self):
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
