'''首先类其实就是一堆函数、变量的打包
只不过设置为本地的话，就是这一组函数间可以直接通信
不然就只能是全局变量了'''
'''
self.setup_ui()
        threading.Thread(target=sys_ctrl.connect, args=(self,), daemon=True).start()
        #用该线程唤醒shockSystem
'''
class ShockSystem:
    def __init__(self):
        self.is_paused = False
        self.ws = None
        self.client_id, self.target_id = None, None
        self.local_ip = "192.168.1.6" # ！！！确保是内网IP！！！
        # localhost? 懒得用
    ''' def __init__()， python内部的函数
    会在挂载的类被加载时运行
    self参数代表这里是 class shockSystem
    如果有class A,B,C,他们自己也可以继续def __init__(self),来有不同的操作
    '''

    def connect(self, ui_app):
        try:
            self.ws = websocket.create_connection("ws://127.0.0.1:9999/")
            self.client_id = json.loads(self.ws.recv()).get('clientId')
            #self.ws.recv()， 没错，received的是json
            #json.loads(...), 是的，python看不明白json，但是能load成字典
            #json.loads(...).get('clientId')， 字典有get这个操作，读键对的值
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

   ''' def connect(self, ui_app):
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
        '''

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
