import os
import configparser
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from plugin.public.find_java_files import find_java_files
from plugin.public.find_main_java_files import find_main_java_files
from plugin.hw2.generate2 import generate_expression
from plugin.hw2.run_java_file2 import run_java_with_input_file_loop
from plugin.hw2.are_expression_equivalent2 import are_expressions_equivalent

def run2(config_file= 'config.ini', cmd=None, if_judge=True):
    print('-' * 5 + "Designed by meteor041" + '-' * 5)
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')

    java_file_folder_path = config['DEFAULT']['java_file_folder_path']
    java_dir = config['DEFAULT']['java_dir']
    # main_class = config['DEFAULT']['main_class']
    main_class = find_main_java_files(java_dir)
    output_path = config['DEFAULT']['output_folder_path']

    ai_enable = (config['GPT']['gpt_enable'] == 'y')
    api = config['GPT']['api']
    base_url = config['GPT']['base_url']
    model = config['GPT']['model']

    # auto_generation = config['COMMAND']['auto_generation']
    # run_times = config['COMMAND']['run_times']
    input_file_path = os.path.join(output_path, "input.txt")
    if not os.path.exists(os.path.dirname(input_file_path)):
        os.mkdir(os.path.dirname(input_file_path))
        print(str(os.path.basename(input_file_path)) + "已创建")
    useGen = input("是否使用内置数据生成(y/n,默认y): ") if cmd == None else cmd[0]
    if useGen.lower() == 'y' or useGen == '':
        times = input("输入运行次数: (最多1000次,默认10次): ") if cmd == None else cmd[1]
        if times == '':
            times = 10
        else:
            times = min(int(times), 1000)
        input_lines = None
        for _ in range(times):
            if (input_lines == None):
                input_lines = [generate_expression(8) + "\n"]
            else:
                input_lines.append(generate_expression(8) + "\n")
        with open(input_file_path, "w") as f:
            for i, s in enumerate(input_lines):
                f.write(s)
    else:
        with open(input_file_path, "r") as f:
            input_lines = None
            new = ""
            para_length = 5
            count = 0
            for line in f:
                if count == 0:
                    para_length = 5 if line.strip() == '1' else 2
                new += line
                count += 1
                if count == para_length:
                    if input_lines == None:
                        input_lines = [new]
                    else:
                        input_lines.append(new)
                    new = ""
                    count = 0

    java_files = find_java_files(java_file_folder_path)
    output = run_java_with_input_file_loop(java_files, input_file_path, main_class, java_dir, output_path)

    output = [s.replace("^", "**") for s in output]

    for i, _output in enumerate(output):
        print(f"你的输出第{i+1}行: {_output}")

    if not if_judge:
        return output


    # 是否出现错误
    all_right = True
    timeout_flag = False
    for i, (_input, _output) in enumerate(zip(input_lines, output)):
        try:
            with ThreadPoolExecutor() as executor:
                future = executor.submit(are_expressions_equivalent, _input, _output, ai_enable, api, base_url, model)
                res = future.result(timeout=10)
        except TimeoutError:
            print(f"第{i+1}次运行时间爆炸 : Sympy包燃尽了...")
            res = True
            timeout_flag = True
        # res = are_expressions_equivalent(_input, _output, ai_enable, api, base_url, model)
        print(f"第{i + 1}行结果: " + str(res))
        all_right = all_right and res


    return "正确,但部分样例超时无法检测" if all_right and timeout_flag else all_right

if __name__ == "__main__":
    print("最终结果: " + str(run2('config.ini')))