import tkinter as tk
from tkinter import filedialog, messagebox
import os
import glob
import subprocess

class GUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Processor")

        # EXE选择按钮
        self.exe_path = tk.StringVar()
        self.exe_path.set("D:/Wukong_PBData_ReadWriter.exe")
        tk.Label(root, text="选择EXE:").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(root, textvariable=self.exe_path, width=50).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(root, text="选择EXE", command=self.select_exe).grid(row=0, column=2, padx=10, pady=10)

        # 复选框：输出到输入同位置
        self.same_location = tk.BooleanVar()
        tk.Checkbutton(root, text="输出到输入同位置", variable=self.same_location, command=self.toggle_output_path).grid(row=0, column=3, padx=10, pady=10)

        # 第一行参数和输入路径
        tk.Label(root, text="输入参数:").grid(row=1, column=0, padx=10, pady=10)
        self.input_param = tk.StringVar()
        self.input_param.set("-inputjson=")
        tk.Entry(root, textvariable=self.input_param, width=20).grid(row=1, column=1, padx=10, pady=10)

        tk.Label(root, text="输入路径:").grid(row=1, column=2, padx=10, pady=10)
        self.input_path = tk.StringVar()
        self.input_path.set("D:/ProtoData")
        tk.Entry(root, textvariable=self.input_path, width=50).grid(row=1, column=3, padx=10, pady=10)
        tk.Button(root, text="选择路径", command=self.select_input_path).grid(row=1, column=4, padx=10, pady=10)

        # 第二行参数和输出路径
        tk.Label(root, text="输出参数:").grid(row=2, column=0, padx=10, pady=10)
        self.output_param = tk.StringVar()
        self.output_param.set("-outputdata=")
        tk.Entry(root, textvariable=self.output_param, width=20).grid(row=2, column=1, padx=10, pady=10)

        tk.Label(root, text="输出路径:").grid(row=2, column=2, padx=10, pady=10)
        self.output_path = tk.StringVar()
        self.output_path.set("D:/ProtoData")
        self.output_path_entry = tk.Entry(root, textvariable=self.output_path, width=50)
        self.output_path_entry.grid(row=2, column=3, padx=10, pady=10)
        tk.Button(root, text="选择路径", command=self.select_output_path).grid(row=2, column=4, padx=10, pady=10)

        # 执行按钮
        tk.Button(root, text="执行", command=self.execute_command).grid(row=3, column=0, columnspan=5, pady=20)

        # 初始状态
        self.toggle_output_path()

    def select_exe(self):
        file_path = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe")])
        if file_path:
            self.exe_path.set(file_path)

    def select_input_path(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.input_path.set(dir_path)
            # 更新输出路径如果复选框被选中
            if self.same_location.get():
                self.update_output_path_from_input()

    def select_output_path(self):
        if not self.same_location.get():
            dir_path = filedialog.askdirectory()
            if dir_path:
                self.output_path.set(dir_path)

    def toggle_output_path(self):
        if self.same_location.get():
            self.output_path_entry.config(state=tk.DISABLED)
        else:
            self.output_path_entry.config(state=tk.NORMAL)

    def update_output_path_from_input(self):
        input_path = self.input_path.get().replace('/', '\\')
        if os.path.isfile(input_path):
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.dirname(input_path)
            self.output_path.set(os.path.join(output_path, base_name))
        elif os.path.isdir(input_path):
            self.output_path.set(input_path)

    def update_input_param(self):
        # Updates the input parameter based on the selected radio button
        choice = self.input_param_choice.get()
        self.input_param.set(choice)

    def generate_output_path(self, json_file):
        """
        根据 JSON 文件路径生成对应的输出路径。
        """
        base_name = os.path.splitext(os.path.basename(json_file))[0]
        output_path = os.path.dirname(json_file)
        return os.path.join(output_path, base_name)

    def execute_command(self):
        exe = self.exe_path.get()
        input_param = self.input_param.get()
        input_path = self.input_path.get().replace('/', '\\')
        output_param = self.output_param.get()
        output_path = self.output_path.get().replace('/', '\\')

        if not exe:
            messagebox.showerror("错误", "请确保EXE路径已填写")
            return

        if input_param == "-inputjson=":
            if not input_path:
                messagebox.showerror("错误", "请输入有效的输入路径")
                return

            # 获取所有JSON文件的路径
            if os.path.isdir(input_path):
                json_files = glob.glob(os.path.join(input_path, '**', '*.json'), recursive=True)
            elif os.path.isfile(input_path) and input_path.endswith('.json'):
                json_files = [input_path]
            else:
                messagebox.showerror("错误", "输入路径无效")
                return

            if not json_files:
                messagebox.showerror("错误", "没有找到JSON文件")
                return

            # 构建命令行参数
            for json_file in json_files:
                json_file = json_file.replace('/', '\\')
                if self.same_location.get():
                    output_file = self.generate_output_path(json_file)
                else:
                    output_file = os.path.join(output_path, os.path.basename(json_file).replace('.json', '.data')).replace('/', '\\')

                command = f'{exe} {input_param}"{json_file}" {output_param}"{output_file}"'

                try:
                    subprocess.run(command, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("错误", f"执行命令时出错: {e}")
                    return

        elif input_param == "-all=":
            # 使用-all参数构建命令，不包括输入路径
            command = f'{exe} {input_param} {output_param}"{output_path}"'

            try:
                subprocess.run(command, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("错误", f"执行命令时出错: {e}")
                return

        messagebox.showinfo("成功", "命令执行完毕")

if __name__ == "__main__":
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()
