# -*- coding: utf-8 -*-
# 阶段一：数据解析与图片下载
# Python 3.8

import json
import requests
import os
import time

# ================= 配置区 =================
BASE_URL = "http://www.yndlsw.com:8001/upload"
RAW_JSON_FILE = "raw_data.json"  # 你从 F12 复制下来的数据文件
OUTPUT_DIR = "images"            # 图片保存文件夹
TASK_FILE = "todo_tasks.json"    # 生成给脚本2用的任务清单
# MY_COOKIE = "这里粘贴你复制的Cookie内容"
#有些会稍微加密一下，要cookie
# ==========================================

def main():
    # 1. 创建图片保存目录
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 2. 读取你从 F12 复制的 JSON 数据
    try:
        with open(RAW_JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 如果外面包了一层 data，就提取里面的列表
            # json文件只对括号敏感，有些神人json很混乱
            records = data.get('data', data) if isinstance(data, dict) else data
    except Exception as e:
        print(f"读取 {RAW_JSON_FILE} 失败，请确认文件是否存在且为合法 JSON: {e}")
        return

    tasks = []
    print(f"成功解析数据，共找到 {len(records)} 条记录。开始下载图片...")

    # 3. 遍历下载图片并整理任务
    # 如果有很弱智的更新直接改下面的名字
    for item in records:
        meter_id = item.get("meterID")
        target_val = item.get("currentReading")
        photo_path = item.get("photoPath")
        customer_name = item.get("customerName", "未知用户")
        
         # 【新增】提取状态字段
        status = item.get("meterReadingFlagName", "")

        # 【核心优化】源头拦截：如果不是“正常”，直接跳过，根本不下载！
        if status != "正常":
            print(f"表号 {meter_id} 状态为 [{status}]，忽略处理。")
            continue

        # 过滤掉没有图片的记录（比如 photoPath 为 null 或者空）
        if not photo_path or "null" in str(photo_path):
            print(f"表号 {meter_id} 无照片，跳过。")
            continue

        img_url = f"{BASE_URL}{photo_path}"
        save_path = os.path.join(OUTPUT_DIR, f"{meter_id}.jpg")

        # 过滤掉没有图片的记录（比如 photoPath 为 null 或者空）
        if not photo_path or "null" in str(photo_path):
            print(f"表号 {meter_id} 无照片，跳过。")
            continue

        img_url = f"{BASE_URL}{photo_path}"
        save_path = os.path.join(OUTPUT_DIR, f"{meter_id}.jpg")

        # 下载逻辑（如果本地已经有了，就不重复下）
        if not os.path.exists(save_path):
            try:
                # stream=True 和 headers 伪装一下浏览器，防止被服务器阻截
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
            
            # 停顿 0.2 秒，防止并发太高垃圾服务器会卡死
            time.sleep(0.2) 
        else:
            print(f"本地已存在，跳过下载: {meter_id}.jpg")

        # 把有效信息塞进任务列表，顺手把状态也带上
        tasks.append({
            "meter_id": meter_id,
            "target_val": str(target_val) if target_val is not None else "",
            "img_path": save_path,
            "customer_name": customer_name,
            "status": status  # 补充进去，保持数据完整
        })

    # 4. 把任务列表保存成 JSON，交给下一个脚本
    with open(TASK_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

    print("\n" + "="*40)
    print(f"脚本 1 执行完毕！")
    print(f"图片已存入 '{OUTPUT_DIR}' 文件夹。")
    print(f"任务清单已生成为 '{TASK_FILE}'。")
    print("="*40)

if __name__ == "__main__":
    main()
