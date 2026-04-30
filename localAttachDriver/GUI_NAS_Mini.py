import os
import io
import zipfile
import socket
import threading
import time
import urllib.parse  # 增加：处理网页传来的字符编码
from http.server import HTTPServer, BaseHTTPRequestHandler
import tkinter as tk
from tkinter import filedialog, ttk


# --- GUI 界面 ---
class MiniNasGui:
    def __init__(self, root):
        self.root = root
        self.root.title("局域网传输 + 文本同步")
        self.root.geometry("600x500")
        
        self.ip_label = tk.Label(self.root, text=f"手机访问: http://{self.get_ip()}:{server_port}", font=("Arial", 12, "bold"), fg="blue")
        #哦对了，python的formatted，甚至允许一个表达式，类似c语言的“谁能写出最难度最短字符代码挑战”，所以可以{self.get_ip()}让python停下来去执行这个函数
        self.ip_label.pack(pady=10)
    
    #关于pack，对于windows来说，gui里塞按钮这样那样必须要是绝对坐标，一拉伸就乱
    #但是Tkinter提供了自动排版引擎pack()，里面的padx\y代表Padding Y-axis / Padding X-axis， 只有一个数值代表上下（y)或左右(x)各留n个像素空，（a,b)代表单独控制
    #self.text_area.pack(padx=10, fill=tk.X)， fill=tk.X代表在横轴拉伸到填满

        # 电脑端的文本框
        tk.Label(root, text="电脑端文本（在此编辑后手机刷新即可见）:").pack()
        
        
        # 创建一个文本框，放在主窗口里，高度是8行文字，字体设为 Consolas
        self.text_area = tk.Text(root, height=8, font=("Consolas", 11))

        # 把内存字典里的文字，插到文本框的最末尾
        self.text_area.insert(tk.END, shared_text["content"])
        #tk.end代表在当前文字的最后。

        # 呼叫自动排版引擎：把文本框按顺序塞进屏幕。
        # 左右留 10 像素的白边 (padx=10)。
        # 把文本框横向拉伸，填满可用宽度 (fill=tk.X)。
        self.text_area.pack(padx=10, fill=tk.X)

if __name__ == "__main__":
    root = tk.Tk()
    #tkinter内也有很多class A,B,C，
    #Tk作为一个类名，Tk()是一个执行类，自动传入了当前内存的地址,给TK的def __init__(self, ...) 
    #实际上，操作的是 tk.TK.__init__(ADDRESS), root = ADDRESS
    app = MiniNasGui(root)
    #实际上，操作的是 miniNasGui__init__(ADDRESS, root), app = ADDRESS
    #这俩的root、app都是对应调用函数的ADDRESS赋给的值
    root.mainloop() #Event Loop,由于root管理了窗口，所以是他来掌控循环
    #mainloop()是Tk类的函数
    #可以tk.Tk().mainloop(),但问题是没法操控这个新窗口了
