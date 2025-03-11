import os
import subprocess
from src.plugin.hw2.are_expression_equivalent2 import are_expressions_equivalent
def run_java_with_input_file_loop(java_files, input_file_path, main_class, java_dir, output_path):
    """
    编译并运行 Java 文件，循环指定次数，每次从输入文件中读取一行作为输入。

    Args:
        java_files: Java 文件路径列表。
        input_file_path: 输入文件的路径。
        main_class: 主类的类名。
        java_dir: Java 文件所在的目录（用于编译和运行）。

    Returns:
        包含每次运行的输出的列表。如果编译失败或运行出错，返回错误信息。
    """
    output_path = os.path.join(output_path, "output.txt")

    try:
        # 1. 编译 Java 文件
        compile_process = subprocess.run(
            ["javac"] + java_files,
            capture_output=True,
            text=True,
            check=True,
            cwd=java_dir
        )

        if compile_process.returncode != 0:
            return f"编译失败:\n{compile_process.stderr}"

        # 2. 读取输入文件行
        with open(input_file_path, "r") as input_file:
            input_lines = input_file.readlines()

        # 3. 循环运行 Java 程序
        outputs = []
        for i, line in enumerate(input_lines):
            line = line.strip()  # 移除行尾的空白字符
            print(f"第 {i+1} 次运行\n输入: {line}")

            process = subprocess.Popen(  # 使用 Popen 来实时输入数据
                ["java", "-cp", java_dir, main_class],
                stdin=subprocess.PIPE,  # 使用管道作为标准输入
                stdout=subprocess.PIPE,  # 获取标准输出
                stderr=subprocess.PIPE,  # 获取标准错误
                text=True,
                cwd=java_dir
            )

            stdout, stderr = process.communicate(input=line) # 将数据写入管道
            #process.wait()

            print(f'输出: {stdout.strip()}')
            if are_expressions_equivalent(line, stdout.replace("^", "**")):
                state = 'Accepted!'
            else:
                state = 'Failed.'
            print(f'{state}\n' + ('-' * 10))

            if process.returncode != 0:
                outputs.append(f"{stderr}".strip())
                try:
                    mode = "w+" if i == 0 else "a"
                    with open(output_path, mode, encoding='utf-8') as f:  # 显式指定编码
                        f.write(f"第 {i+1} 次运行报错: {stderr.strip()}\n")
                except Exception as e:
                    print(f"写入文件时发生错误: {e}")  # 打印错误信息
            else:
                outputs.append(f"{stdout}".strip())
                try:
                    mode = "w+" if i == 0 else "a"
                    with open(output_path, mode, encoding='utf-8') as f:  # 显式指定编码
                        f.write(f"第 {i+1} 次运行 {state}: {stdout.strip()}\n")
                except Exception as e:
                    print(f"写入文件时发生错误: {e}")  # 打印错误信息

        return outputs  # 返回所有运行的输出

    except subprocess.CalledProcessError as e:
        return f"错误:\n{e.stderr}"
    except FileNotFoundError as e:
        return f"文件未找到错误:\n{e}"
    except Exception as e:
        return f"其他错误:\n{e}"