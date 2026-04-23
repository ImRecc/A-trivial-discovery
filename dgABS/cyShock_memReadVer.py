import tkinter as tk
from tkinter import ttk, messagebox
import threading, time, json, websocket, qrcode, random, os
from PIL import ImageTk, Image

# ================= 1. 配置与波形解析 =================
VAL_FILE = r"D:\DGL_socket\game_val.txt"

def load_waves():
    try:
        with open('DG_WAVES_V2_V3_simple.js', 'r', encoding='utf-8') as f:
            content = f.read()
        start, end = content.find('['), content.rfind(']') + 1
        wave_list = json.loads(content[start:end])
        # 建立映射：名字 -> expectedV3 数组
        return {item['name']: item['expectedV3'] for item in wave_list if 'expectedV3' in item}
    except Exception as e:
        print(f"波形加载失败: {e}")
        return {"默认波形": ["0A0A0A0A64646464"]}

ALL_WAVES = load_waves()
WAVE_NAMES = list(ALL_WAVES.keys())

# ================= 2. 郊狼控制中心 (融合版) =================
class ShockSystem:
    def __init__(self):
        self.is_paused = False
        self.ws = None
        self.client_id, self.target_id = None, None
        self.local_ip = "192.168.1.6" # ！！！确保是内网IP！！！
        # localhost? 懒得用

    def connect(self, ui_app):
        try:
            self.ws = websocket.create_connection("ws://127.0.0.1:9999/")
            self.client_id = json.loads(self.ws.recv()).get('clientId')
            qr_text = f"https://www.dungeon-lab.com/app-download.php#DGLAB-SOCKET#ws://{self.local_ip}:9999/{self.client_id}"
            ui_app.show_qr(qr_text)
            
            while True:
                msg = json.loads(self.ws.recv())
                # 兼容 200 响应和 bind 类型
                if (msg.get("message") == "200" or msg.get("type") == "bind") and "targetId" in msg:
                    self.target_id = msg.get("targetId")
                    ui_app.on_ready()
                    break
        except Exception as e: print(f"网络异常: {e}")

    def connect(self, ui_app):
        try:
            self.ws = websocket.create_connection("ws://127.0.0.1:9999/")
            # 视觉版获取 ID 的方式
            self.client_id = json.loads(self.ws.recv()).get('clientId')
            qr_text = f"https://www.dungeon-lab.com/app-download.php#DGLAB-SOCKET#ws://{self.local_ip}:9999/{self.client_id}"
            ui_app.show_qr(qr_text)
            
            while True:
                msg = json.loads(self.ws.recv())
                # 视觉版判断绑定的逻辑
                if msg.get("message") == "200" and "targetId" in msg:
                    self.target_id = msg.get("targetId")
                    ui_app.on_ready()
                    break
        except Exception as e: print(f"网络异常: {e}")

    def send(self, wave_pool, duration, strength_raw, channel_mode):
        """
        完全复刻你发给我的视觉版 send 逻辑
        """
        if not self.target_id or self.is_paused: return
        
        # 强度解析逻辑（保留我们现在的随机功能）
        try:
            s_str = str(strength_raw)
            if '-' in s_str:
                low, high = map(int, s_str.split('-'))
                strength = random.randint(low, high)
            else:
                strength = int(s_str)
        except: strength = 10

        try:
            # --- 关键：复刻视觉版波形提取 ---
            wave_name = random.choice(wave_pool)
            # 这里 wave_data 必须是 json 字符串化的列表
            wave_data = json.dumps(ALL_WAVES.get(wave_name, list(ALL_WAVES.values())[0]))
            
            # 确定通道
            targets = []
            if "A" in channel_mode: targets.append(("A", 1))
            if "B" in channel_mode: targets.append(("B", 2))
            
            for ch_name, ch_idx in targets:
                # 1. 设置强度 (完全复刻视觉版格式)
                self.ws.send(json.dumps({
                    "type": 3, 
                    "channel": ch_idx, 
                    "strength": strength, 
                    "clientId": self.client_id, 
                    "targetId": self.target_id, 
                    "message": "set channel"
                }))
                time.sleep(0.05) # 视觉版延迟
                
                # 2. 发送波形 (完全复刻视觉版格式：裸发 clientMsg)
                self.ws.send(json.dumps({
                    "type": "clientMsg", 
                    "channel": ch_name, 
                    "time": float(duration), 
                    "message": f"{ch_name}:{wave_data}", 
                    "clientId": self.client_id, 
                    "targetId": self.target_id
                }))
                time.sleep(0.05) # 视觉版延迟
                
            print(f"⚡ [复刻版下发] 波形:{wave_name} | 强度:{strength}")
        except Exception as e: 
            print(f"发送失败: {e}")

sys_ctrl = ShockSystem()

# ================= 3. GUI 控制台 (视觉增强版) =================
class BridgeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("赛博刑具 V4.4 - 深度兼容版")
        self.root.geometry("1100x700")
        self.root.configure(bg="#2b2b2b") 
        self.last_val = None
        self.slots = []

        if not os.path.exists(os.path.dirname(VAL_FILE)):
            os.makedirs(os.path.dirname(VAL_FILE))

        self.setup_ui()
        threading.Thread(target=sys_ctrl.connect, args=(self,), daemon=True).start()
        threading.Thread(target=self.watch_file, daemon=True).start()

    def setup_ui(self):
        # 顶部
        top = tk.Frame(self.root, bg="#1e1e1e", pady=15)
        top.pack(fill=tk.X)
        self.val_lbl = tk.Label(top, text="等待内存数据...", fg="#00ff00", bg="#1e1e1e", font=("Consolas", 18, "bold"))
        self.val_lbl.pack()

        main = tk.Frame(self.root, bg="#2b2b2b")
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        left_panel = tk.Frame(main, bg="#2b2b2b")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for i in range(3):
            slot_frame = tk.LabelFrame(left_panel, text=f"规则槽位 {i+1}", bg="#3c3f41", fg="#ffffff", pady=15, padx=15)
            slot_frame.pack(fill=tk.X, pady=8)

            s = {
                "en": tk.BooleanVar(value=False), "mode": tk.StringVar(value="降低"),
                "target": tk.DoubleVar(value=0), "chan": tk.StringVar(value="A"),
                "strg": tk.StringVar(value="20-40"), "dur": tk.DoubleVar(value=1.5),
                "waves": []
            }

            # 修复黑色看不见的问题：绿色高亮
            tk.Checkbutton(slot_frame, text="启用规则", variable=s['en'], bg="#3c3f41", fg="#00ff00", 
                           selectcolor="#000", activebackground="#3c3f41", font=("微软雅黑", 10, "bold")).grid(row=0, column=0, padx=5)
            
            ttk.Combobox(slot_frame, textvariable=s['mode'], values=["降低", "增加", "等于"], width=6).grid(row=0, column=1, padx=5)
            tk.Entry(slot_frame, textvariable=s['target'], width=8, bg="#4e5052", fg="white").grid(row=0, column=2)
            
            tk.Label(slot_frame, text="通道:", bg="#3c3f41", fg="#ccc").grid(row=0, column=3, padx=5)
            ttk.Combobox(slot_frame, textvariable=s['chan'], values=["A", "B", "A+B"], width=5).grid(row=0, column=4)

            tk.Label(slot_frame, text="强度范围:", bg="#3c3f41", fg="#ccc").grid(row=0, column=5, padx=5)
            tk.Entry(slot_frame, textvariable=s['strg'], width=10, bg="#4e5052", fg="white").grid(row=0, column=6)

            tk.Label(slot_frame, text="秒:", bg="#3c3f41", fg="#ccc").grid(row=0, column=7, padx=5)
            tk.Entry(slot_frame, textvariable=s['dur'], width=4, bg="#4e5052", fg="white").grid(row=0, column=8)

            btn = tk.Button(slot_frame, text="设置波形(0)", bg="#4b6eaf", fg="white", width=12)
            btn.config(command=lambda b=btn, idx=i: self.pick_waves(idx, b))
            btn.grid(row=0, column=9, padx=10)
            
            self.slots.append(s)

        # 右侧
        right_panel = tk.Frame(main, bg="#1e1e1e", width=260)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        right_panel.pack_propagate(False)
        
        tk.Label(right_panel, text="郊狼扫码连接", fg="white", bg="#1e1e1e").pack(pady=15)
        self.qr_lbl = tk.Label(right_panel, text="等待网络...", bg="#1e1e1e", fg="#666")
        self.qr_lbl.pack(pady=10)
        self.st_lbl = tk.Label(right_panel, text="状态: 离线", fg="#ff4444", bg="#1e1e1e", font=("微软雅黑", 10, "bold"))
        self.st_lbl.pack()

    def watch_file(self):
        while True:
            if os.path.exists(VAL_FILE):
                try:
                    with open(VAL_FILE, "r") as f:
                        content = f.read().strip()
                        if content:
                            cur_val = float(content)
                            self.val_lbl.config(text=f"内存数值: {cur_val}")
                            if self.last_val is not None:
                                for s in self.slots:
                                    if not s['en'].get(): continue
                                    triggered = False
                                    mode = s['mode'].get()
                                    if mode == "降低" and cur_val < self.last_val: triggered = True
                                    elif mode == "增加" and cur_val > self.last_val: triggered = True
                                    elif mode == "等于" and cur_val == s['target'].get(): triggered = True
                                    
                                    if triggered and s['waves']:
                                        threading.Thread(target=sys_ctrl.send, 
                                                       args=(s['waves'], s['dur'].get(), s['strg'].get(), s['chan'].get()), 
                                                       daemon=True).start()
                            self.last_val = cur_val
                except: pass
            time.sleep(0.1)

    def pick_waves(self, idx, btn):
        win = tk.Toplevel(self.root)
        win.title("波形选择")
        lb = tk.Listbox(win, selectmode=tk.MULTIPLE, width=40, height=20, bg="#2b2b2b", fg="white")
        lb.pack(padx=10, pady=10)
        for n in WAVE_NAMES: lb.insert(tk.END, n)
        for i, n in enumerate(WAVE_NAMES):
            if n in self.slots[idx]['waves']: lb.select_set(i)
        def save():
            self.slots[idx]['waves'] = [lb.get(i) for i in lb.curselection()]
            btn.config(text=f"已选({len(self.slots[idx]['waves'])})", bg="#2ecc71")
            win.destroy()
        tk.Button(win, text="确定", command=save, bg="#2ecc71").pack(fill=tk.X)

    def show_qr(self, txt):
        img = qrcode.make(txt).resize((200, 200))
        self.root.qr_img = ImageTk.PhotoImage(img)
        self.qr_lbl.config(image=self.root.qr_img, text="")

    def on_ready(self):
        self.st_lbl.config(text="● 郊狼已在线", fg="#00ff00")
        messagebox.showinfo("OK", "App 已连接！")

if __name__ == "__main__":
    root = tk.Tk()
    app = BridgeGUI(root)
    root.mainloop()
