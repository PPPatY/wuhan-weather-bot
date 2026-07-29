#!/usr/bin/env python3
"""
武汉天气 Telegram Bot
每天早上 7:30 推送当天天气预报
"""

import os
import time
import requests
from datetime import datetime

# 从环境变量读取（GitHub Actions 会注入）
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def get_wuhan_weather() -> str:
    """获取武汉天气（wttr.in API）"""
    url = "https://wttr.in/Wuhan?format=3&lang=zh"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        return f"⚠️ 天气获取失败：{e}"

def send_to_telegram(text: str, max_retries: int = 3):
    """发送消息到 Telegram（带重试机制）"""
    if not BOT_TOKEN or not CHAT_ID:
        raise ValueError("BOT_TOKEN 或 CHAT_ID 未设置")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }

    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔄 尝试发送消息 (第 {attempt}/{max_retries} 次)...")
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            print(f"✅ 消息已发送：{text[:50]}...")
            return
        except requests.exceptions.Timeout:
            print(f"⏱ 请求超时 (第 {attempt} 次)")
            if attempt < max_retries:
                wait_time = attempt * 2
                print(f"⏳ 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                print(f"❌ 重试 {max_retries} 次后仍然失败")
                raise
        except Exception as e:
            print(f"❌ 发送失败：{e}")
            raise

if __name__ == "__main__":
    # 生成日期字符串
    now = datetime.now()
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    date_str = f"{now.strftime('%Y-%m-%d')} {weekdays[now.weekday()]}"

    # 获取天气
    weather = get_wuhan_weather()

    # 构造消息
    message = f"""🌤 <b>武汉天气日报</b>
📅 {date_str}

{weather}

<i>每日 7:30 自动推送</i>"""

    # 发送到 Telegram
    send_to_telegram(message)
