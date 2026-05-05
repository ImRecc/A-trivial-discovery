# -*- coding: utf-8 -*-
# 阶段一：数据下载与预处理 (V2 过滤增强版)
import json
import requests
import os
import time

# ================= 配置区 =================
BASE_URL = "http://www.yndlsw.com:8001/upload"
RAW_JSON_FILE = "raw_data.json"  # F12 复制下来的原始数据[cite: 2]
OUTPUT_DIR = "images"            # 图片保存文件夹
TASK_FILE = "todo_tasks.json"    # 生成给脚本2用的任务清单[cite: 2]
# ==========================================

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    try:
        with open(RAW_JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 兼容不同格式的 JSON[cite: 2]
            records = data.get('data', data) if isinstance(data, dict) else data
    except Exception as e:
        print(f"读取 {RAW_JSON_FILE} 失败: {e}")
        return

    tasks = []
    skipped_count = 0
    total_records = len(records)
    
    print(f"解析成功，共 {total_records} 条。开始处理...")
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

    start_time = time.time()
    
    for i, item in enumerate(records):
        # --- 新增过滤逻辑 ---
        reading_flag = item.get("meterReadingFlagName")
        if reading_flag == "无人":
            skipped_count += 1
            continue # 直接跳过这条记录
        # ------------------

        meter_id = item.get("meterID")
        target_val = item.get("currentReading") # 后续由 clean_target 处理[cite: 4]
        photo_path = item.get("photoPath")
        customer_name = item.get("customerName", "未知用户")
        
        # 基础校验：如果没有路径或路径无效则跳过
        if not photo_path or "null" in str(photo_path):
            continue

        img_url = f"{BASE_URL}{photo_path}"
        save_path = os.path.join(OUTPUT_DIR, f"{meter_id}.jpg")

        # 检查本地是否已存在，支持断点续传
        if not os.path.exists(save_path):
            try:
                response = session.get(img_url, timeout=5)
                if response.status_code == 200:
                    with open(save_path, 'wb') as img_f:
                        img_f.write(response.content)
                    if i % 50 == 0:
                        print(f"进度: {i}/{total_records} | 下载中: {meter_id}")
                else:
                    print(f"下载失败({response.status_code}): {meter_id}")
            except Exception as e:
                print(f"连接跳过 {meter_id}: {e}")
        
        # 将有效任务加入清单
        tasks.append({
            "meter_id": meter_id,
            "target_val": str(target_val) if target_val is not None else "",
            "img_path": save_path,
            "customer_name": customer_name
        })

    # 保存任务清单供 st2_nvidia_v6.py 使用[cite: 2]
    with open(TASK_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

    end_time = time.time()
    print("\n" + "="*40)
    print(f"执行完毕！")
    print(f"原始总数: {total_records}")
    print(f"因‘无人’跳过: {skipped_count}")
    print(f"最终生成任务: {len(tasks)}")
    print(f"总耗时: {int(end_time - start_time)} 秒")
    print(f"任务清单: {TASK_FILE}")
    print("="*40)

if __name__ == "__main__":
    main()
