# -*- coding: utf-8 -*-
# 自动原型 b-0.35 - 
# 适配环境：Python 3.8.10 (Win32) / Windows 7
# 功能：云端手写体识别 + 正则数据清洗 + 逻辑相似度裁决

import requests
import base64
import re
import sys
import json
from difflib import SequenceMatcher

# 禁用 SSL 警告（解决 Win7 根证书过期问题）
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================== 配置区域 ==================
API_KEY = ""
SECRET_KEY = ""
# ============================================
# 【自定义阈值】最低可接受的相似度（0.7 代表 70% 匹配即可通过）
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
        # verify=False 是为了跳过 Win7 的证书验证
        response = requests.get(url, params=params, verify=False, timeout=10)
        return response.json().get("access_token")
    except Exception as e:
        print(f"【系统错误】Token获取失败，请检查网络或SK配置: {e}")
        return None

def call_baidu_handwriting(img_path, token):
    """调用百度手写识别接口"""
    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/handwriting?access_token={token}"
    
    try:
        with open(img_path, "rb") as f:
            img_data = base64.b64encode(f.read())
        
        # probability=true 强制要求返回置信度
        payload = {
            "image": img_data,
            "probability": "true" 
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        response = requests.post(url, headers=headers, data=payload, verify=False, timeout=20)
        return response.json()
    except Exception as e:
        print(f"【系统错误】图片处理或请求超时: {e}")
        return None

def process_table_data(ocr_result):
    """核心清洗逻辑"""
    raw_lines = []
    confidences = []
    
    words_result = ocr_result.get("words_result", [])
    for item in words_result:
        word = item.get("words", "")
        raw_lines.append(word)
        
        # 提取百度返回的平均置信度 (0-1之间)
        prob = item.get("probability", {}).get("average", 0)
        confidences.append(prob)
    
    full_text = "".join(raw_lines)
    # 使用正则只保留数字
    pure_numbers = "".join(re.findall(r"\d+", full_text))
    #用正则表达式 \d+ 把所有的汉字、字母、标点全扔掉，只留下数字
    
    avg_conf = sum(confidences) / len(confidences) if confidences else 0
    return full_text, pure_numbers, avg_conf, raw_lines

def main():
    # 接收来自 BAT 的参数
    if len(sys.argv) < 3:
        print("用法提示：请将图片拖入 BAT 脚本并输入对比数字")
        return

    target_num = sys.argv[1]
    img_path = sys.argv[2]
    # sys.argv[0]是程序自己的名字，比如meter_ocr_final.py

    print("--- 尝试连接ocr服务 ---")
    token = get_access_token()
    if not token: 
        return

    result = call_baidu_handwriting(img_path, token)
    if not result or "words_result" not in result:
        print("【识别失败】未能从图片中提取到文字内容")
        return

    full_text, ocr_num, confidence, lines = process_table_data(result)

    # 计算字符串相似度（基于莱文斯坦距离）
    #要把字符串 A 变成字符串 B，最少需要插、删、换几次？
    sim_score = SequenceMatcher(None, target_num, ocr_num).ratio()

    print("\n" + "="*40)
    print(f"【原始数据流】: {full_text}")
    print(f"【识别到行数】: {len(lines)} 行")
    print(f"【清洗后数字】: {ocr_num}")
    print(f"【期望比对值】: {target_num}")
    print("-" * 40)

    # 逻辑裁决体系
    if target_num == ocr_num:
        print("判定结果：【完全匹配】")
    elif target_num in ocr_num:
        print("判定结果：【包含匹配】（AI可能多读了边框噪点）")
    elif sim_score > MIN_ACCEPT_SIMILARITY:
        print(f"判定结果：【高度疑似】（相似度: {sim_score:.1%}）")
    else:
        print("判定结果：【不匹配】 需人工核实")

    print(f"【置信度】  : {confidence:.2%}")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
