# -*- coding: utf-8 -*-
import json
import requests
import os
import time

# ================= 配置区 =================
BASE_URL = "http://www.yndlsw.com:8001/upload"
RAW_JSON_FILE = "raw_data.json"  # F12 复制下来的数据文件
OUTPUT_DIR = "images"            # 图片保存文件夹
TASK_FILE = "todo_tasks.json"    # 生成给脚本2用的任务清单
# ==========================================

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    try:
        with open(RAW_JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 兼容不同格式的 JSON
            records = data.get('data', data) if isinstance(data, dict) else data
    except Exception as e:
        print(f"读取 {RAW_JSON_FILE} 失败: {e}")
        return

    tasks = []
    print(f"解析成功，共 {len(records)} 条。开始极致单线程下载...")
    
    # 建立 Session 可以复用 TCP 连接，提速明显且对服务器更友好
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

    start_time = time.time()
    
    for i, item in enumerate(records):
        meter_id = item.get("meterID")
        target_val = item.get("currentReading")
        photo_path = item.get("photoPath")
        customer_name = item.get("customerName", "未知用户")
        
        if not photo_path or "null" in str(photo_path):
            continue

        img_url = f"{BASE_URL}{photo_path}"
        save_path = os.path.join(OUTPUT_DIR, f"{meter_id}.jpg")

        if not os.path.exists(save_path):
            try:
                # 这里的 timeout 缩短到 5 秒，单线程最怕卡死
                response = session.get(img_url, timeout=5)
                
                if response.status_code == 200:
                    with open(save_path, 'wb') as img_f:
                        img_f.write(response.content)
                    # 减少打印频率（每10张印一次），打印也是占时间的
                    if i % 10 == 0:
                        print(f"进度: {i}/{len(records)} | 下载成功: {meter_id}")
                else:
                    print(f"下载失败({response.status_code}): {meter_id}")
            except Exception as e:
                print(f"连接跳过 {meter_id}: {e}")
        
        # 已删除 time.sleep(0.2)，单线程下载过程本身就是天然的频率限制
        
        tasks.append({
            "meter_id": meter_id,
            "target_val": str(target_val) if target_val is not None else "",
            "img_path": save_path,
            "customer_name": customer_name
        })

    with open(TASK_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

    end_time = time.time()
    print("\n" + "="*40)
    print(f"执行完毕！总耗时: {int(end_time - start_time)} 秒")
    print(f"任务清单: {TASK_FILE}")
    print("="*40)

if __name__ == "__main__":
    main()
