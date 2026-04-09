# -*- coding: utf-8 -*-
# Python 3.8.10 (Win32) / Windows 7
# 最终版逻辑：状态过滤 -> 自动转正图片 -> 极简特征提取 -> CSV直接比对输出

import json
import csv
import time
import requests
import base64
import re
from difflib import SequenceMatcher
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= 配置区 =================
API_KEY = ""
SECRET_KEY = ""
TASK_FILE = "todo_tasks.json" 
RESULT_FILE = "audit_report_final.csv"
# ==========================================

def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    try:
        response = requests.get(url, params=params, verify=False, timeout=10)
        return response.json().get("access_token")
    except:
        return None

def call_baidu_ocr(img_path, token):
    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/meter?access_token={token}"
    try:
        with open(img_path, "rb") as f:
            img_data = base64.b64encode(f.read())
        
        payload = {
            "image": img_data,
            "probability": "true",
            "detect_direction": "true"  # 核心修改：强制开启AI自动倒转图片检测
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        response = requests.post(url, headers=headers, data=payload, verify=False, timeout=20)
        return response.json()
    except:
        return None

def extract_best_number(ocr_result, target_num):
    """弱化置信度权重，只提取最优数字串返回给 CSV 供人类比对"""
    words_result = ocr_result.get("words_result", [])
    best_candidate = ""
    max_sim = 0
    all_raw_lines = []

    for item in words_result:
        text = item.get("words", "")
        all_raw_lines.append(text)
        current_num = "".join(re.findall(r"\d+", text))
        if not current_num: 
            continue
            
        sim = SequenceMatcher(None, target_num, current_num).ratio()
        if sim > max_sim:
            max_sim = sim
            best_candidate = current_num

    # 兜底：如果单行没提出数字，暴力拼接所有字符再提取
    if not best_candidate:
        full_text = "".join(all_raw_lines)
        best_candidate = "".join(re.findall(r"\d+", full_text))

    return best_candidate

def main():
    token = get_access_token()
    if not token: 
        return
        
    with open(TASK_FILE, 'r', encoding='utf-8') as f:
        tasks = json.load(f)

    with open(RESULT_FILE, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        # 简化表头：去除置信度等冗余数据，直接排布对比列
        writer.writerow(["表号", "用户名", "系统期望值", "AI识别值", "直接比对", "图片路径"])
        
        for task in tasks:
            # 核心修改：拦截非“正常”状态的数据
            #status = task.get("meterReadingFlagName", "")
            #if status != "正常":
            #    continue
                
            m_id = task.get("meter_id", "")
            target = str(task.get("target_val", ""))
            img_p = task.get("img_path", "")
            name = task.get("customer_name", "")

            print(f"正在处理：{name}({m_id})->目标值:{target}")
            ocr_res = call_baidu_ocr(img_p, token)
            
            if ocr_res and "words_result" in ocr_res:
                ai_num = extract_best_number(ocr_res, target)
            else:
                ai_num = "请求/识别失败"

            # 极简核对逻辑：完全一致标"√"，有偏差标"X"交由人工复核
            match_res = "√" if ai_num == target else "X"
            
            writer.writerow([m_id, name, target, ai_num, match_res, img_p])
            
            # 核心修改：适配 QPS 10，每次请求间隔 0.15 秒留出容错余量
            time.sleep(0.15) 

if __name__ == "__main__":
    main()
