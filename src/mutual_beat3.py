# 批量测试工具
import os
from concurrent.futures import ThreadPoolExecutor
from plugin.hw2.generate2 import generate_expression
from run2 import run2
import configparser
from sympy import *
import random
x = symbols('x')
count = 1
eps = 1e-6
auto_generate=False
def batchRun(config_list_path):
    res = list()
    for root, dirs, files in os.walk(config_list_path):
        for i, file in enumerate(files):
            # if i != 7:
            #     continue
            con = os.path.join(root, file)
            print(f"第{i+1}个测试对象:" + con)
            with ThreadPoolExecutor() as executor:
                future = executor.submit(run2, con, ['n'], if_judge=False)
                try:
                    res.append(future.result(timeout=60))
                except TimeoutError:
                    # print(f"第{i + 1}次运行时间爆炸 : Sympy包燃尽了...")
                    future.cancel()
                    res.append('timeout')
                    # executor.shutdown(wait=False)  # 不等待线程完成，立即关闭线程池
    # res为8xn列表
    print(f"---测试最终结果：{res}---".format(res=res))

    # 生成一个随机值代入x
    random_value = random.uniform(-10, 10)

    encounter_error_sentences = False

    num_columns = len(res[0]) if res else 0
    # 遍历每一行
    for col_idx in range(num_columns):
        evaluated_values = []
        for row in res:
            expr = row[col_idx] if col_idx < len(row) else None
            try:
                # 尝试将表达式转换为符号表达式并代入随机值
                evaluated_value = sympify(expr).subs(x, random_value)
                evaluated_values.append(evaluated_value)
            except (SympifyError, TypeError, AttributeError):
                # 如果转换失败，替换为114，并设置标志变量为True
                evaluated_values.append(114)
                encounter_error_sentences = True
        # 检查同一行的所有元素在代入x后的值是否相等
        if all(abs(val-evaluated_values[0]) < eps for val in evaluated_values) and not encounter_error_sentences:
            print(f"Row {col_idx+1}: All expressions \033[1;32m are equal when x = {random_value}\033[0m")
        else:
            print(f"Row {col_idx+1}: Expressions are \033[1;31m NOT equal when x = {random_value}\033[0m")
        print(["%.2f" % num for num in evaluated_values])

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("config.ini", encoding='utf-8')
    input_file_path = config['BEAT']['input_file_path']
    log_file_path = config['BEAT']['log_file_path']
    if auto_generate:
        # 随机生成count条数据
        lines = ''
        for _ in range(count):
            lines += generate_expression() +'\n'
    else:
        # 读取用户设置的输入
        with open("input_file_path", 'r') as f:
            lines = f.readlines()
    for i in range(1,10):
        file_path = os.path.join(input_file_path, "log%d" % i, "input.txt")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.writelines(lines)


    config_list_path = config['BEAT']['config_folder_path']
    batchRun(config_list_path)