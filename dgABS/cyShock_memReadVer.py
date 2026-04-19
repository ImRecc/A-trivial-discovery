import pymem
import pymem.process
import time

class MemoryMonitor:
    def __init__(self, process_name, base_offset, offsets):
        """
        初始化内存读取器
        :param process_name: 游戏进程名，例如 "StellarBlade.exe"
        :param base_offset: 基址偏移 (通常是 "游戏.exe" + 一个十六进制偏移)
        :param offsets: 指针偏移链表，例如 [0x28, 0x50, 0x1A4]
        """
        self.process_name = process_name
        self.base_offset = base_offset
        self.offsets = offsets
        self.pm = None
        self.client_base = None
        self.last_hp = -1  # 记录上次的血量

    def attach_game(self):
        """尝试挂载游戏进程"""
        try:
            self.pm = pymem.Pymem(self.process_name)
            # 获取游戏主模块的基址
            client_module = pymem.process.module_from_name(self.pm.process_handle, self.process_name)
            self.client_base = client_module.lpBaseOfDll
            print(f"✅ 成功挂载游戏: {self.process_name}")
            return True
        except pymem.exception.ProcessNotFound:
            print(f"等待游戏运行: {self.process_name}...")
            return False

    def get_pointer_addr(self):
        """核心计算：通过基址和多级偏移计算出当前的真实内存地址"""
        if not self.pm: return None
        
        try:
            # 第一步：读取基址里的值
            addr = self.pm.read_longlong(self.client_base + self.base_offset) # 如果是32位游戏用 read_int
            
            # 第二步：依次加上偏移量并读取下一个指针
            for offset in self.offsets[:-1]:
                addr = self.pm.read_longlong(addr + offset)
                
            # 最后一步：加上最后一个偏移量，这就是存放真实血量的地址
            return addr + self.offsets[-1]
        except Exception as e:
            # 游戏加载画面或切换场景时，指针可能会断裂
            return None

    def read_hp(self):
        """读取当前血量"""
        addr = self.get_pointer_addr()
        if addr:
            try:
                # 假设血量是 4字节整数 (如果是浮点数，改成 read_float)
                hp = self.pm.read_int(addr) 
                return hp
            except:
                return -1
        return -1

    def trigger_shock(self, intensity="轻度"):
        """你的郊狼触发逻辑放在这里"""
        print(f"⚡ [郊狼发力] 触发了 {intensity} 电击！")
        # TODO: 接入你原来的向郊狼发包的代码

    def run(self):
        print("🚀 内存监听器启动...")
        while True:
            # 1. 确保游戏在运行
            if not self.pm:
                self.attach_game()
                time.sleep(2)
                continue

            # 2. 读取当前血量
            current_hp = self.read_hp()

            if current_hp != -1:
                # 第一次读取，初始化血量
                if self.last_hp == -1:
                    self.last_hp = current_hp
                    print(f"🔍 初始血量锁定: {self.last_hp}")

                # 3. 核心判定逻辑
                if current_hp < self.last_hp:
                    damage = self.last_hp - current_hp
                    print(f"🩸 受到伤害: 扣除 {damage} 点血量 (当前: {current_hp})")
                    
                    if current_hp <= 0:
                        print("💀 角色死亡！")
                        self.trigger_shock(intensity="致命最大")
                        # 死亡后可能需要等待复活，防止疯狂电击
                        time.sleep(5) 
                        self.last_hp = -1 # 重置状态以便下一命
                    else:
                        self.trigger_shock(intensity="轻度/中度")
                    
                elif current_hp > self.last_hp:
                    print(f"💖 回血了 (当前: {current_hp})")
                
                self.last_hp = current_hp
            
            # 每秒检测几十次即可，不需要占用太多 CPU
            time.sleep(0.05)


if __name__ == "__main__":
    # ================= 配置区 =================
    # 【警告】以下数值必须你在 CE 里自己找出来填进去！
    
    GAME_EXE = "YourGame.exe"  # 你的游戏进程名
    
    # 假设你在 CE 找到的绿字是："YourGame.exe"+0x01A2B3C4
    BASE_OFFSET = 0x01A2B3C4 
    
    # 假设你在 CE 找到的偏移链是 0x10, 0x258, 0x80
    OFFSETS = [0x10, 0x258, 0x80] 
    
    # ==========================================

    monitor = MemoryMonitor(GAME_EXE, BASE_OFFSET, OFFSETS)
    monitor.run()
