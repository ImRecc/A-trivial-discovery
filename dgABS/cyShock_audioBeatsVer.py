import numpy as np
import tkinter as tk
from tkinter import Toplevel, Checkbutton, ttk
import threading, time, json, websocket, qrcode, random, warnings
from PIL import ImageTk, Image
import soundcard as sc

warnings.filterwarnings("ignore")

# ================= 1. 加载波形 =================
def load_waves():
    try:
        with open('DG_WAVES_V2_V3_simple.js', 'r', encoding='utf-8') as f:
            content = f.read()
        start, end = content.find('['), content.rfind(']') + 1
        wave_list = json.loads(content[start:end])
        return {item['name']: item['expectedV3'] for item in wave_list if 'expectedV3' in item}
    except Exception as e:
        print("波形加载失败，使用默认:", e)
        return {"默认波形": ["0A0A0A0A00000000", "0A0A0A0A64646464"]}

ALL_WAVES = load_waves()
WAVE_NAMES = list(ALL_WAVES.keys())

# ================= 2. 郊狼控制中心 =================
class ShockSystem:
    def __init__(self):
        self.is_paused = False
        self.locked_until = {"A": 0, "B": 0}
        self.ws = None
        self.client_id = None
        self.target_id = None
        self.local_ip = "192.168.1.6"   # ←←← 改成你电脑的实际内网IP

    def connect(self, ui_app):
        try:
            self.ws = websocket.create_connection("ws://127.0.0.1:9999/")
            msg = json.loads(self.ws.recv())
            self.client_id = msg.get('clientId')
            qr_text = f"https://www.dungeon-lab.com/app-download.php#DGLAB-SOCKET#ws://{self.local_ip}:9999/{self.client_id}"
            ui_app.root.after(0, ui_app.show_qr_image, qr_text)
            
            while True:
                msg = json.loads(self.ws.recv())
                if msg.get("message") == "200" and "targetId" in msg:
                    self.target_id = msg.get("targetId")
                    ui_app.root.after(0, ui_app.on_ready)
                    break
        except Exception as e:
            print(f"连接异常: {e}")

    def send_shock(self, wave_pool, duration, strength, channel_mode):
        if self.is_paused or not self.target_id or not wave_pool:
            return

        now = time.time()
        targets = []
        if "A" in channel_mode: targets.append(("A", 1))
        if "B" in channel_mode: targets.append(("B", 2))

        can_fire = all(now > self.locked_until[name] for name, _ in targets)
        if not can_fire:
            return

        try:
            wave_name = random.choice(wave_pool)
            wave_data = json.dumps(ALL_WAVES.get(wave_name, list(ALL_WAVES.values())[0]))
            final_str = max(1, int(strength))

            for ch_name, ch_idx in targets:
                self.ws.send(json.dumps({
                    "type": 3, "channel": ch_idx, "strength": final_str,
                    "clientId": self.client_id, "targetId": self.target_id, "message": "set channel"
                }))
                time.sleep(0.03)

                self.ws.send(json.dumps({
                    "type": "clientMsg", "channel": ch_name, "time": duration,
                    "message": f"{ch_name}:{wave_data}",
                    "clientId": self.client_id, "targetId": self.target_id
                }))
                time.sleep(0.03)

                self.locked_until[ch_name] = now + 3.0
        except Exception as e:
            print(f"发送失败: {e}")

sys_ctrl = ShockSystem()

# ================= 3. 主界面（已修复滑块实时控制虚线） =================
class AudioVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("赛博刑具 V3.8 - 音频随动版（3秒冷却 + 实时阈值线）")
        self.root.geometry("1150x780")
        self.root.configure(bg="#050505")

        self.bass_waves = []
        self.vocal_waves = []

        self.setup_ui()
        self.start_connection()
        threading.Thread(target=self.audio_engine, daemon=True).start()

    def setup_ui(self):
        # 频谱画布
        self.canvas = tk.Canvas(self.root, width=1050, height=280, bg="#000", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.bars = [self.canvas.create_rectangle(i*21, 280, i*21+17, 280, fill="#1db954", outline="") for i in range(50)]
        
        # 两条可拖动的阈值线
        self.line_bass = self.canvas.create_line(0, 280-140, 1050, 280-140, fill="#00aaff", width=2, dash=(5,3))
        self.line_vocal = self.canvas.create_line(0, 280-190, 1050, 280-190, fill="#ff4757", width=2, dash=(5,3))

        main = tk.Frame(self.root, bg="#050505")
        main.pack(fill=tk.BOTH, expand=True, padx=20)

        # 左侧控制区
        lf = tk.Frame(main, bg="#111", width=200)
        lf.grid(row=0, column=0, sticky="nsew", padx=5)
        self.qr_lbl = tk.Label(lf, text="加载中...", bg="#111", fg="white")
        self.qr_lbl.pack(pady=10)
        self.st_lbl = tk.Label(lf, text="● 离线", bg="#111", fg="gray")
        self.st_lbl.pack()

        self.btn_pause = tk.Button(lf, text="暂停/继续", command=self.toggle_pause, bg="#333", fg="white", height=2)
        self.btn_pause.pack(pady=8, fill=tk.X)

        # 低音 & 人声配置（滑块已绑定实时更新虚线）
        self.s_bass, self.c_bass = self.make_config_box(main, "低音 (Bass)", "#00aaff", 0, 1)
        self.s_vocal, self.c_vocal = self.make_config_box(main, "人声/中高频", "#ff4757", 0, 2)

        # 全局设置
        rf = tk.LabelFrame(main, text=" 全局增益 & 限制 ", fg="gold", bg="#050505")
        rf.grid(row=0, column=3, sticky="nsew", padx=5)
        tk.Label(rf, text="整体灵敏度", fg="white", bg="#050505").pack()
        self.s_gain = tk.Scale(rf, from_=300, to_=50, orient=tk.HORIZONTAL, bg="#050505", fg="white", length=220)
        self.s_gain.set(160); self.s_gain.pack(pady=5)
        tk.Label(rf, text="最大强度上限", fg="gold", bg="#050505").pack()
        self.s_limit = tk.Scale(rf, from_=100, to_=10, orient=tk.HORIZONTAL, bg="#050505", fg="gold", length=220)
        self.s_limit.set(45); self.s_limit.pack()

    def make_config_box(self, parent, title, color, r, c):
        f = tk.LabelFrame(parent, text=title, fg=color, bg="#050505")
        f.grid(row=r, column=c, sticky="nsew", padx=8, pady=5)
        
        s = tk.Scale(f, from_=280, to_=0, orient=tk.VERTICAL, length=220, bg="#050505", fg="white",
                     command=self.sync_threshold_lines)   # ← 关键绑定
        s.set(140 if "低音" in title else 190)
        s.pack(side=tk.LEFT, padx=5)
        
        tk.Label(f, text="通道:", bg="#050505", fg="gray").pack(pady=(15,0))
        cb = ttk.Combobox(f, values=["通道 A", "通道 B", "双通道"], width=12, state="readonly")
        cb.set("通道 A" if "低音" in title else "通道 B")
        cb.pack(pady=5)
        
        tk.Button(f, text="选择波形", command=lambda: self.pick_waves(title), bg="#333", fg="white").pack(pady=15)
        return s, cb

    # ================= 实时更新两条阈值线 =================
    def sync_threshold_lines(self, _=None):
        # 低音滑块控制蓝色线
        bass_y = 280 - self.s_bass.get()
        self.canvas.coords(self.line_bass, 0, bass_y, 1050, bass_y)
        
        # 人声滑块控制红色线
        vocal_y = 280 - self.s_vocal.get()
        self.canvas.coords(self.line_vocal, 0, vocal_y, 1050, vocal_y)

    def pick_waves(self, mode):
        win = Toplevel(self.root)
        win.title("选择波形池")
        canvas = tk.Canvas(win, width=280)
        scroll = tk.Scrollbar(win, command=canvas.yview)
        frame = tk.Frame(canvas)
        canvas.create_window((0,0), window=frame, anchor="nw")
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        vars_list = []
        cur_list = self.bass_waves if "低音" in mode else self.vocal_waves
        for name in WAVE_NAMES:
            v = tk.BooleanVar(value=name in cur_list)
            Checkbutton(frame, text=name, variable=v, bg="#111", fg="white", selectcolor="#1db954").pack(anchor="w", padx=10, pady=2)
            vars_list.append((name, v))
        
        def save():
            selected = [n for n, v in vars_list if v.get()]
            if "低音" in mode:
                self.bass_waves = selected
            else:
                self.vocal_waves = selected
            win.destroy()
        
        tk.Button(win, text="确定", command=save, bg="#1db954", fg="black").pack(fill=tk.X, pady=5)
        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def toggle_pause(self):
        sys_ctrl.is_paused = not sys_ctrl.is_paused
        self.btn_pause.config(text="【已暂停】" if sys_ctrl.is_paused else "暂停/继续",
                              bg="#500" if sys_ctrl.is_paused else "#333")

    def start_connection(self):
        threading.Thread(target=sys_ctrl.connect, args=(self,), daemon=True).start()

    def show_qr_image(self, text):
        img = qrcode.make(text).resize((160, 160))
        self.root.qr_img = ImageTk.PhotoImage(img)
        self.qr_lbl.config(image=self.root.qr_img, text="")

    def on_ready(self):
        self.st_lbl.config(text="● 已连接", fg="#1db954")

    def audio_engine(self):
        try:
            mic = sc.get_microphone(id=sc.default_speaker().name, include_loopback=True)
            with mic.recorder(samplerate=44100, blocksize=4096) as recorder:
                while True:
                    if sys_ctrl.is_paused:
                        time.sleep(0.1)
                        continue
                        
                    data = recorder.record(numframes=2048)
                    samples = data[:, 0]
                    fft = np.abs(np.fft.rfft(samples)) * 1.8
                    
                    gain = self.s_gain.get()
                    bar_heights = [np.log10(fft[i+1] + 1) * gain for i in range(50)]
                    for i in range(50):
                        h = np.clip(bar_heights[i], 0, 280)
                        self.canvas.coords(self.bars[i], i*21, 280-h, i*21+17, 280)
                    
                    bass_energy = np.max(bar_heights[1:8])
                    vocal_energy = np.max(bar_heights[12:32])
                    limit = self.s_limit.get()
                    
                    if bass_energy > self.s_bass.get():
                        ratio = min(1.0, (bass_energy - self.s_bass.get()) / max(1, 280 - self.s_bass.get()))
                        strength = int(limit * (0.5 + 0.5 * ratio))
                        threading.Thread(target=sys_ctrl.send_shock, 
                                         args=(self.bass_waves, random.randint(1, 4), strength, self.c_bass.get()), 
                                         daemon=True).start()
                    
                    if vocal_energy > self.s_vocal.get():
                        ratio = min(1.0, (vocal_energy - self.s_vocal.get()) / max(1, 280 - self.s_vocal.get()))
                        strength = int(limit * (0.5 + 0.5 * ratio))
                        threading.Thread(target=sys_ctrl.send_shock, 
                                         args=(self.vocal_waves, random.randint(1, 4), strength, self.c_vocal.get()), 
                                         daemon=True).start()
                    
                    time.sleep(0.012)
        except Exception as e:
            print(f"音频引擎异常: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioVisualizer(root)
    root.mainloop()
