# -*- coding: utf-8 -*-
# 自动化流水线 阶段二：AI 批量识别与比对
# 适配环境：Python 3.8 + Windows 7

import json
import csv
import time
# 之前那个 OCR 脚本的核心逻辑函数
# OCR 函数名 call_baidu_meter_ocr 和 process_table_data
from meter_ocr_final_meterVer import get_access_token, call_baidu_meter_ocr, process_table_data

# ================= 配置区 =================
TASK_FILE = "todo_tasks.json"     # 脚本1生成的清单
RESULT_FILE = "audit_report.csv"  # 最终的对账报表
# ==========================================

def main():
    # 1. 初始化 Token
    print("--- 正在连接服务... ---")
    token = get_access_token()
    if not token: 
        print("Token 获取失败，请检查 API Key 和网络。")
        return

    # 2. 加载任务单
    try:
        with open(TASK_FILE, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
    except Exception as e:
        print(f"找不到任务清单 {TASK_FILE}，请先运行脚本 1。")
        return

    print(f"开始处理 {len(tasks)} 个比对任务...")

    # 3. 准备 CSV 报表
    with open(RESULT_FILE, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['表号', '用户名', '系统期望值', 'AI识别值', '判定结果', '置信度', '图片路径']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # 4. 循环处理
        for i, task in enumerate(tasks):
            m_id = task['meter_id']
            target = task['target_val']
            img_p = task['img_path']
            name = task['customer_name']

            print(f"[{i+1}/{len(tasks)}] 正在识别表号: {m_id}...")

            # 调用你之前的 OCR 逻辑
            ocr_res = call_baidu_meter_ocr(img_p, token)
            
            if ocr_res and "words_result" in ocr_res:
                # 使用你之前写的 process_table_data 函数
                _, best_num, conf, sim = process_table_data(ocr_res, target)
                
                # 判定逻辑
                if best_num == target:
                    verdict = "完全匹配"
                elif sim >= 0.7:
                    verdict = "高度疑似"
                else:
                    verdict = "不匹配"
            else:
                best_num = "识别失败"
                verdict = "无效图片"
                conf = 0

            # 写入一行结果
            writer.writerow({
                '表号': m_id,
                '用户名': name,
                '系统期望值': target,
                'AI识别值': best_num,
                '判定结果': verdict,
                '置信度': f"{conf:.2%}",
                '图片路径': img_p
            })

            # 百度基础版 API 往往有并发限制，QPS一般为2
            # 建议每秒处理不超过2张，防止报错
            time.sleep(0.5)

    print("\n" + "="*40)
    print(f"全部处理完毕！")
    print(f"审计报表已生成: {RESULT_FILE}")
    print("="*40)

if __name__ == "__main__":
    main()
