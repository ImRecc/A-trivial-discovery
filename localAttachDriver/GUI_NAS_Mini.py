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

if __name__ == "__main__":
    root = tk.Tk()
    #tkinter内也有很多class A,B,C，
    #Tk作为一个类名，Tk()是一个执行之类
    #
    app = MiniNasGui(root)
    root.mainloop() #Event Loop,由于root管理了窗口，所以是他来掌控循环
