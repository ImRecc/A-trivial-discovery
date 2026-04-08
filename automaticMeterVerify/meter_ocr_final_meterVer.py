# -*- coding: utf-8 -*-
# 自动原型 b-0.41 (语法修正版)
# 适配环境：Python 3.8.10 (Win32) / Windows 7
# 功能：百度仪表OCR + 逐行相似度筛选 + 正则清洗 + 逻辑判定

import requests
import base64
import re
import sys
import json
from difflib import SequenceMatcher

# 禁用 SSL 警告（解决 Win7 根证书过期导致 API 连不上的问题）
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================== 配置区域 ==================
API_KEY = ""
SECRET_KEY = ""

# 【最低可接受相似度】低于此值将判定为不匹配
MIN_ACCEPT_SIMILARITY = 0.7 
# ============================================

def get_access_token():
    """获取百度 OAuth2.0 Token"""
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": SECRET_KEY
    }
    try:
        # verify=False 绕过 Win7 证书验证
        response = requests.get(url, params=params, verify=False, timeout=10)
        return response.json().get("access_token")
    except Exception as e:
        print(f"【系统错误】Token 获取失败: {e}")
        return None

def call_baidu_meter_ocr(img_path, token):
    """调用百度仪器仪表识别 API"""
    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/meter?access_token={token}"
    
    try:
        with open(img_path, "rb") as f:
            img_data = base64.b64encode(f.read())
        
        #probability强制返回置信度
        payload = {
            "image": img_data,
            "probability": "true" 
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        response = requests.post(url, headers=headers, data=payload, verify=False, timeout=20)
        return response.json()
    except Exception as e:
        print(f"【网络错误】API 请求失败: {e}")
        return None

'''def process_table_data(ocr_result, target_num):
    """
    核心清洗与筛选逻辑
    作用：从 OCR 返回的一堆文字里，挑出最像 target_num 的那个候选者
    """
    words_result = ocr_result.get("words_result", [])
    
    best_candidate = ""
    max_sim_found = 0
    #confidences = []
    best_confidence = 0  # 替换原有的 confidences 列表
    all_raw_lines = []

    for item in words_result:
        word_text = item.get("words", "")
        all_raw_lines.append(word_text)
        
        # 1. 提取当前行中的纯数字 (修正了这里引起报错的语法)
        current_num_str = "".join(re.findall(r"\d+", word_text))
        if not current_num_str:
            continue
            
        # 2. 计算这一行数字与目标值的相似度
        sim = SequenceMatcher(None, target_num, current_num_str).ratio()
        
        # 3. 筛选最优解（谁最像目标值，就认准谁）
        if sim > max_sim_found:
            max_sim_found = sim
            best_candidate = current_num_str
            
        # 记录置信度
        prob = item.get("probability", {}).get("average", 0)
        confidences.append(prob)
        # 汇总数据
    full_text_snapshot = " | ".join(all_raw_lines)
    avg_conf = sum(confidences) / len(confidences) if confidences else 0
    
    # 兜底：如果逐行都没找到有数字的内容，尝试合并后的全局提取
    if not best_candidate:
        best_candidate = "".join(re.findall(r"\d+", full_text_snapshot))
        max_sim_found = SequenceMatcher(None, target_num, best_candidate).ratio()

    return full_text_snapshot, best_candidate, avg_conf, max_sim_found
    '''
def process_table_data(ocr_result, target_num):
    """
    核心清洗与筛选逻辑
    """
    words_result = ocr_result.get("words_result", [])
    
    best_candidate = ""
    max_sim_found = 0
    best_confidence = 0  # 替换原有的 confidences 列表
    all_raw_lines = []

    for item in words_result:
        word_text = item.get("words", "")
        all_raw_lines.append(word_text)
        
        current_num_str = "".join(re.findall(r"\d+", word_text))
        if not current_num_str:
            continue
            
        sim = SequenceMatcher(None, target_num, current_num_str).ratio()
        
        # 当发现更优的相似度匹配时，同步记录该行的置信度
        if sim > max_sim_found:
            max_sim_found = sim
            best_candidate = current_num_str
            best_confidence = item.get("probability", {}).get("average", 0)

    full_text_snapshot = " | ".join(all_raw_lines)
    
    if not best_candidate:
        best_candidate = "".join(re.findall(r"\d+", full_text_snapshot))
        max_sim_found = SequenceMatcher(None, target_num, best_candidate).ratio()

    # 返回 best_confidence 替代原来的 avg_conf
    return full_text_snapshot, best_candidate, best_confidence, max_sim_found

    

def main():
    # 检查命令行参数 (由 BAT 脚本传入)
    if len(sys.argv) < 3:
        print("用法提示: 请将图片拖入脚本并输入对比数字")
        return

    target_num = sys.argv[1]
    img_path = sys.argv[2]

    print("--- 正在连接云端服务... ---")
    token = get_access_token()
    if not token: return

    # 发起识别
    result = call_baidu_meter_ocr(img_path, token)
    if not result or "words_result" not in result:
        print("【识别失败】未能从图片中提取到任何数据")
        return

    # 数据处理与最优匹配筛选
    full_text, ocr_num, confidence, sim_score = process_table_data(result, target_num)

    # 打印报告
    print("\n" + "="*40)
    print(f"【识别原文】: {full_text}")
    print(f"【提取数字】: {ocr_num}")
    print(f"【期望比对】: {target_num}")
    print("-" * 40)

    # 执行逻辑决策
    if target_num == ocr_num:
        print("判定结果：【完全匹配】")
    elif target_num in ocr_num and len(ocr_num) <= len(target_num) + 2:
        # 应对多识别了边框或小数点的微小干扰
        print("判定结果：【基本一致】 (包含匹配)")
    elif sim_score >= MIN_ACCEPT_SIMILARITY:
        print(f"判定结果：【高度疑似】 (相似度: {sim_score:.1%})")
    else:
        print("判定结果：【不匹配】 需人工核实")

    print(f"【AI 置信度】: {confidence:.2%}")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
