# -*- coding: utf-8 -*-
import os
import io
import zipfile
import socket
import threading
import time
import urllib.parse
import uuid  # 用于生成不重复的随机ID
import email # 引入原生邮件库，它是解析 HTTP 多文件上传的绝佳工具
import email.parser
from http.server import HTTPServer, BaseHTTPRequestHandler
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

# --- 全局配置 ---
UPLOAD_DIR = "uploaded_files"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 扫盲：get请求，会是GET /download/123456 HTTP/1.1
#这串会被切开形成 /download/123456 存入BaseHTTPRequestHandler.path
#.startswith() 是python的字符串的内置方法，判定某段字是不是某字符串的开头

shared_items = {}
shared_text = {"content": "在这里输入文字，点击同步..."}
#python的字典，或者叫哈希表，
#getDicKeyValue=dicName["keyName"]
#可以这么用来获取字典内部键对应的值
server_port = 8000

class TransparentSharingHandler(BaseHTTPRequestHandler):
#class 名字(爹的名字): 是创建一个“富二代”类
#继承他爹的东西
#然后自己定义或者重写了如下do_GET,do_POST
    def do_GET(self):
        print(self.headers)
        if self.path.startswith("/download/"):
            item_id = self.path.split("/")[-1]
            if item_id in shared_items:
                real_path = shared_items[item_id]
                if os.path.isfile(real_path):
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    # 处理中文文件名乱码
                    encoded_name = urllib.parse.quote(os.path.basename(real_path))
                    self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{encoded_name}")
                    self.end_headers()
                    with open(real_path, 'rb') as f: self.wfile.write(f.read())
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        items_html = "" # 先准备一个空字符串
        # 遍历那个叫 shared_items 的哈希表（字典）
        # tid 是文件的6位随机ID，p 是文件在电脑上的绝对路径（比如 C:/abc/test.txt）
        for tid, p in shared_items.items():
    
            # os.path.basename 的作用是：把 "C:/abc/test.txt" 里的 "test.txt" 抠出来
            filename = os.path.basename(p) 
    
            # 拼凑一段 HTML 代码
            # <a> 标签在 HTML 里就是“超链接”。href 是点击后跳转的网址。
            # <li> 是列表的一行。
            html_line = f'<li>{filename} <a href="/download/{tid}">[下载]</a></li>'
    
            # 把这一行追加到总字符串里
            items_html = items_html + html_line
        
        # 或者可以装逼一点
        # items_html = "".join([f'<li>{os.path.basename(p)} <a href="/download/{tid}">[下载]</a></li>' for tid, p in shared_items.items()])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1">
        <!-- adaptive scaling, insides of <head> are invisible -->
        <style>
            body {{ font-family:sans-serif; padding:20px; background:#f4f4f9; }}
            .card {{ background:white; padding:15px; border-radius:8px; margin-bottom:15px; box-shadow:0 2px 5px rgba(0,0,0,0.1); }}
            textarea {{ width:100%; height:120px; box-sizing: border-box; }}
            .btn {{ padding:10px 15px; background:#4CAF50; color:white; border:none; border-radius:4px; cursor:pointer; }}
        <!-- .xxx{{}} means class, can be re-use for a same style -->
        </style>
        </head>
        <body>
            <h3>局域网同步站</h3>
            
            <div class="card">
                <h4>文本同步</h4>
                <textarea id="text_box">{shared_text["content"]}</textarea><br>
                <!-- {shared_text["content"]}，这是 Python 在发网页前，强行把内存里的字塞进去了。 -->
                <button class="btn" onclick="syncText()" style="margin-top:10px;">↑↓ 同步文本</button>
            </div>

            <div class="card">
                <h4>批量上传文件到电脑</h4>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <!-- 这里加上了 multiple 属性，允许手机/网页多选文件 -->
                    <input type="file" name="files" multiple style="margin-bottom:10px;"><br>
                    <!-- -->
                    <input type="submit" value="一键上传全部" class="btn" style="background:#2196F3;">
                </form>
            </div>

            <div class="card">
                <h4>电脑共享的资源:</h4>
                <ul>{items_html if items_html else "暂无共享"}</ul>
            </div>
            
            <script>
                function syncText() {{
                    var content = document.getElementById('text_box').value;
                    <!--去网页上找到那个文本框，把里面的字抠出来，存到 content 变量里。-->
                    fetch('/sync_text', {{ method: 'POST', body: encodeURIComponent(content) }})
                    <!--异步请求fetch，不用手动刷新-->
                    .then(() => alert('已推送到电脑！'));
                }}
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))
        # 用utf8编码写入html，python把http连接也看作文件，所以是wfile

    def do_POST(self):
        if self.path == "/sync_text":
            length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(length).decode('utf-8')
            shared_text["content"] = urllib.parse.unquote(post_data)
            #urllib的意义是把%E4%BD%A0%E5%A5%BD%20%E4%B8%96%E7%95%8C这种的url编码翻译回中文与空格
            self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
            return

        # ================= 核心升级：使用 email 库优雅解析多文件 =================
        if self.path == "/upload":
            try:
                length = int(self.headers['Content-Length'])
                raw_body = self.rfile.read(length)
                print(raw_body)
                
                # 伪造一个邮件头部，欺骗 email.parser 帮我们解析 HTTP 表单流
                mime_msg = b"Content-Type: " + self.headers['Content-Type'].encode() + b"\r\n\r\n" + raw_body
                msg = email.parser.BytesParser().parsebytes(mime_msg)
                
                # 遍历所有被传上来的文件
                if msg.is_multipart():
                    for part in msg.get_payload():
                        # 获取原生文件名并处理中文
                        raw_filename = part.get_param('filename', header='content-disposition')
                        if raw_filename:
                            # 确保文件名是正确的字符串
                            filename = str(email.header.make_header(email.header.decode_header(raw_filename)))
                            save_path = os.path.join(UPLOAD_DIR, filename)
                            
                            # 写入文件
                            with open(save_path, 'wb') as f:
                                f.write(part.get_payload(decode=True))
                            print(f"成功接收文件: {filename}")
                
                self.send_response(303) # 上传完自动刷新页面
                self.send_header('Location', '/')
                self.end_headers()
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Upload Failed: {e}".encode())

class MiniNasGui:
    def __init__(self, root):
        self.root = root
        self.root.title("局域网传输 + 批量文件接收器")
        self.root.geometry("600x600")
        
        
        self.ip_label = tk.Label(self.root, text=f"手机访问: http://{self.get_ip()}:{server_port}", font=("Arial", 12, "bold"), fg="blue")
        #哦对了，python的formatted，甚至允许一个表达式，类似c语言的“谁能写出最难度最短字符代码挑战”，所以可以{self.get_ip()}让python停下来去执行这个函数
        self.ip_label.pack(pady=10)
        #关于pack，对于windows来说，gui里塞按钮这样那样必须要是绝对坐标，一拉伸就乱
        #但是Tkinter提供了自动排版引擎pack()，里面的padx\y代表Padding Y-axis / Padding X-axis， 只有一个数值代表上下（y)或左右(x)各留n个像素空，（a,b)代表单独控制
        #self.text_area.pack(padx=10, fill=tk.X)， fill=tk.X代表在横轴拉伸到填满

        # 创建一个文本框，放在主窗口里，高度是8行文字，字体设为 Consolas
        self.text_area = tk.Text(root, height=8, font=("Consolas", 11))

        # 把内存字典里的文字，插到文本框的最末尾
        self.text_area.insert(tk.END, shared_text["content"])
        #tk.end代表在当前文字的最后。

        # 呼叫自动排版引擎：把文本框按顺序塞进屏幕。
        # 左右留 10 像素的白边 (padx=10)。
        # 把文本框横向拉伸，填满可用宽度 (fill=tk.X)。
        self.text_area.pack(padx=10, fill=tk.X)

         #pack()留空时，它的默认参数是 side=tk.TOP。意思是：从上往下，像摞砖头一样居中堆叠
        #ide 参数的可选值只有四个：tk.TOP, tk.BOTTOM, tk.LEFT, tk.RIGHT（上下左右）

        tk.Button(root, text="保存文本到内存", command=self.save_text, bg="#e1f5fe").pack(pady=5)
        
        self.info_label = tk.Label(root, text=f"上传目录: {os.path.abspath(UPLOAD_DIR)}", fg="green")
        self.info_label.pack(pady=5)

        self.tree = ttk.Treeview(root, columns=("ID", "Path"), show="headings", height=5)
        self.tree.heading("ID", text="ID"); self.tree.heading("Path", text="路径")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10)

        btn_fm = tk.Frame(root)
        btn_fm.pack(pady=10)
        # 把按钮名字改了以作区分
        tk.Button(btn_fm, text="+批量共享文件", command=self.add_multiple_files).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_fm, text="打开上传文件夹", command=lambda: os.startfile(UPLOAD_DIR)).pack(side=tk.LEFT, padx=5)

        self.check_sync()
        threading.Thread(target=self.run_server, daemon=True).start()

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try: s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]
        except: ip = "127.0.0.1"
        finally: s.close()
        return ip

    def save_text(self):
        shared_text["content"] = self.text_area.get("1.0", tk.END).strip()
        #("1.0", tk.END).strip()
        #意思是第一行第0列的字符，到最后，.strip()用于清洗字符串，把字符串开头和结尾的换行符 \n、回车符 \r、空格全砍掉
        messagebox.showinfo("成功", "已存入内存，手机刷新可见！")

    def check_sync(self):
    # 简单的比对逻辑：如果内存内容和文本框内容不一样，说明手机推新东西了
        current_in_mem = shared_text["content"]
        current_in_gui = self.text_area.get("1.0", tk.END).strip()
        '''if current_in_mem != current_in_gui:
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, current_in_mem)
        '''
         # 只有当内存里的内容变了，且当前文本框没有被鼠标选中（没在打字）时，才更新GUI
        if current_in_mem != current_in_gui:
            # 获取当前哪个控件拥有焦点
            if self.root.focus_get() != self.text_area: 
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, current_in_mem)

        self.root.after(1000, self.check_sync)
        #目前的问题在于：每秒强制检查，意味着输入方需要在一秒内完成输入与上传，逻辑有问题
        #GUI 的 mainloop 是一个死循环，如果你用 time.sleep(1)，整个窗口就会卡死无响应。after(1000, 函数) 是 Tkinter 提供的不卡死定时器，
        #抽空执行一下 self.check_sync”。函数末尾又调了一次 after，形成了一个每秒执行一次的轮询（Polling）。

    # ================= 核心升级：电脑端多选文件 =================
    def add_multiple_files(self):
        # 注意这里多了一个 's'，返回的是一个元组 (包含多个路径)
        file_paths = filedialog.askopenfilenames(title="请选择一个或多个文件")
        if file_paths:
            for p in file_paths:
                # 使用 uuid 生成唯一的 6 位 ID，防止多文件同时导入时 ID 冲突
                tid = uuid.uuid4().hex[:6]
                shared_items[tid] = p
                self.tree.insert("", tk.END, values=(tid, p))

    def run_server(self):
        HTTPServer(('0.0.0.0', server_port), TransparentSharingHandler).serve_forever()
        #(a, b) 这种的是python的元组，固定长度的数组
        #def HTTPServer(tuple(server_address, server_port), RequestHandlerClass)
        '''在python里，一个类，className(),是照着图纸建一栋房子，把房子的地址给我
            className，不带括号，意思是“把图纸本身交给我”传递参数
        '''

if __name__ == "__main__":
    root = tk.Tk()
    #tkinter内也有很多class A,B,C，
    #Tk作为一个类名，Tk()是一个执行之类
    #实际上，操作的是 tk.TK.__init__(ADDRESS), ADDRESS=&root
    instantApp = MiniNasGui(root)
    #实际上，操作的是 miniNasGui.__init__(ADDRESS, root), ADDRESS=&instantApp
    
    root.mainloop() #Event Loop,由于root管理了窗口，所以是他来掌控循环
    #mainloop()是Tk类的函数
    #可以tk.Tk().mainloop(),但问题是没法操控这个新窗口了
