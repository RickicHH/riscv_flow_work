
# 1 核心功能

dvrun 脚本是一个flow脚本，能够通过解析传入的参数进行仿真。有些参数是必须的有些参数是非必选项目。主要的功能为：
1. 对指定模块进行仿真
2. 对指定test 进行仿真
3. random seed可以控制，也可以指定
4. 能够读取项目配置 project.cfg
5. rerun dump波形
6. 渲染.j2文件
7. 基于多线程的regression 控制thread
8. 编译，仿真过程的控制
# 2 传入的参数

# 3 flow流程
flow的流程由simulator.yaml来控制，该文件定义了文件的编译以及仿真过程.
dvrun会按顺序依次执行,调用相应的脚本，脚本中的控制条件输入由命令行提供。
dvrun执行以后，依次生成vcs_cfg.mk 和Makefile， <test_name>\_run.sh 最终dvrun会启动shell，开始编译仿真。

主要过程如下所示：
```
  1> python publish.py -module <cwd> -out <cwd> 
  output: mv DE files like .v to rtl , mv DV files like .sv to test

  2> python post_publish.py -module <cwd> -out <cwd>  
  output: vcs_cfg.mk and Makefile

  3> make analysis > vlogan.log

  4> make compile > compile.log

  5> make tool_chain_compile > compile.log

  4> make simulation > run.log

  5> python post_sim.py  >run.log
```
 
 flow_work 文件结构为：
 ```
├── dvrun.py
├── infra
│   ├── scripts
│   │   ├── flow
│   │   │   ├── common_scripts
│   │   │   │   ├── lib.py
│   │   │   ├── publish.py
│   │   │   └── simulator.yaml
│   │   │   └── result_analysis.py
│   │   └── uvmgen
│   ├── template
│   └── tool_chain
├── __init__.py
├── Makefile
├── project.cfg
├── README.md
├── requirements.txt
├── src
│   ├── rtl
│   └── verify
│       ├── cfg
│       ├── cov
│       ├── env
│       ├── reg
│       ├── seq
│       ├── tb
│       │   └── c_testlib.yaml
│       └── test
├── template
└── yaml
    ├── base_test_share.yaml
    ├── c_test_share.yaml
    ├── README.md
    └── simulator.yaml

```

## 3.1 publish过程

publish过程主要是pre_compile ，用于准备需要编译的文件，包含提取test list，将test中的配置属性进行归类，生成中间文件。为了具有一定的扩展性，publish过程支持.j2文件渲染。

publish脚本有两种运行模式：
1. 本地运行，单独调用

**you must specify 3 arguments**: publish_src, publish_out, flow_config     
**example**:
```
python3 publish.py -source ./src -out ./publish -config_list ./project.cfg
```
``
2. 通过dvrun调用

```
publish = Publish(
os.path.join(os.environ["RISCV_DV_ROOT"],'src'),
os.environ["RISCV_DV_PUBLISH_OUT"],
os.path.join(os.environ["RISCV_DV_ROOT"],'project.cfg')
)
publish.start()
```
### 3.1.1 test list
1. test list 有两个C_list && UVM_list
2. test list 定义在test_yaml路径下，每一个模块定义一个test_yaml, 比如bus_test.yaml.
3. 有一个base_share.yaml ，用来储存共同的通用的配置， 如果某一个test需要使用，只需要extend它就可以了: 定义了father_test_name, 会根据test_name和father_test_name 进行递归，将test_option 和 regression tag 进行merge, 将父类的option和tag都贴到child test 对应的item中。具体的流程为：
	1. get  c_test_dict  uvm_test_dict
	2. get base_test_share
	3. copy and merge father test_option  to child test_option and regression tag
	4. 输出两个final_test_list : uvm_final_test_list & c_final_test_list
	5. 判断args是否有定义test case ， 如果有，判断是否存在于final_test_list中，如果args没有定义args，判断一下args中是否定义了regr_tag，如果有，按照args.regr_tag来筛选出regression_test_list. 
4. 最后产生两个final test list.
### 3.1.2 .j2 render
### 3.1.3 config publish
## 3.2 tool chain compile
## 3.3 VCS tree- step
### 3.3.1 analysis
### 3.3.2 pre-compile
### 3.3.3 compile
### 3.3.4 Simulation
### 3.3.5 post_sim



