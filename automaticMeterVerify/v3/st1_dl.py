# -*- coding: utf-8 -*-
# 阶段一：数据解析与图片下载
# Python 3.8
'''json的格式：
{
  "data": [
    { "meterID": "710300011", "currentReading": 533.00, ... },
    { "meterID": "710300022", "currentReading": 120.00, ... }
  ],
  "draw": 3,
  "recordsTotal": 1968
}
'''

import json
import requests
import os
import time

# ================= 配置区 =================
BASE_URL = "http://www.yndlsw.com:8001/upload"
RAW_JSON_FILE = "raw_data.json"  # 你从 F12 复制下来的数据文件
OUTPUT_DIR = "images"            # 图片保存文件夹
TASK_FILE = "todo_tasks.json"    # 生成给脚本2用的任务清单
# ==========================================

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    try:
        with open(RAW_JSON_FILE, 'r', encoding='utf-8') as f:
        # with会在离开划定的区域后，立马f.close()，依靠缩进判定
        # open(filename, r\w\a(append) mode, encoding(utf\GBK不能读中文)
            data = json.load(f)
        #json.load(f)会把f给翻译成python内部数据结构，比如字典型{}或列表[]
            records = data.get('data', data) if isinstance(data, dict) else data
        # 判定data.get('data', data)是不是字典型
        #如果是字典型就找找里面键名叫'data'的，找到就把键名为'data'的东西的值拉出来给records
        #因为有些json是{"data": [{"id": 1}, {"id": 2}]}这个样子（比如这个项目的raw_data.json就这样）
        
    except Exception as e:
        print(f"读取 {RAW_JSON_FILE} 失败，请确认文件是否存在且为合法 JSON: {e}")
        return
    #try区域内的任意失败，则执行，e作为错误信息

    tasks = []
    print(f"成功解析数据，共找到 {len(records)} 条记录。开始下载图片...")

    for item in records:
        meter_id = item.get("meterID")
        target_val = item.get("currentReading")
        photo_path = item.get("photoPath")
        customer_name = item.get("customerName", "未知用户")
        #没错，字典里的{1:k1,2:k2,...}都是键-值对应的
        
        # 如果需要过滤状态，就看着加
        status = item.get("meterReadingFlagName", "")
        if status != "正常": continue
        # "meterReadingFlagName":"\u6B63\u5E38" | "1"
        # encoding=utf-8会翻译这个为“正常”
        # 很神秘就是了


        # 修改 st1 里的读取逻辑
        status = item.get("meterReadingFlagName", "未知") # 拿不到就默认是“未知”
        # 或者干脆不判断它，直接下载，反正有 meterID 就能下
        
        if not photo_path or "null" in str(photo_path):
            print(f"表号 {meter_id} 无照片，跳过。")
            continue

        img_url = f"{BASE_URL}{photo_path}"
        save_path = os.path.join(OUTPUT_DIR, f"{meter_id}.jpg")

        if not os.path.exists(save_path):
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                response = requests.get(img_url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    with open(save_path, 'wb') as img_f:
                        img_f.write(response.content)
                    print(f"下载成功: {meter_id}.jpg")
                else:
                    print(f"下载失败 (状态码 {response.status_code}): {meter_id}")
            except Exception as e:
                print(f"网络异常 {meter_id}: {e}")
            
            time.sleep(0.2) 
        else:
            print(f"本地已存在，跳过下载: {meter_id}.jpg")

        tasks.append({
            "meter_id": meter_id,
            "target_val": str(target_val) if target_val is not None else "",
            "img_path": save_path,
            "customer_name": customer_name
        })

    with open(TASK_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

    print("\n" + "="*40)
    print("脚本 1 执行完毕！")
    print(f"图片已存入 '{OUTPUT_DIR}' 文件夹。")
    print(f"任务清单已生成为 '{TASK_FILE}'。")
    print("="*40)

if __name__ == "__main__":
    main()
