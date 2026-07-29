#!/usr/bin/env python3
"""
武汉天气 Telegram Bot
每天早上 7:30 推送未来三天天气预报（和风天气API）
"""

import os
import time
import requests
from datetime import datetime

# 从环境变量读取（GitHub Actions 会注入）
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
QWEATHER_KEY = os.environ.get("QWEATHER_KEY")  # 和风天气 API Key

# 调试输出（不会泄露完整key）
print(f"🔍 环境变量检查：")
print(f"  BOT_TOKEN: {'✅ 已设置' if BOT_TOKEN else '❌ 未设置'}")
print(f"  CHAT_ID: {'✅ 已设置' if CHAT_ID else '❌ 未设置'}")
print(f"  QWEATHER_KEY: {'✅ 已设置 (前6位: ' + QWEATHER_KEY[:6] + '...)' if QWEATHER_KEY else '❌ 未设置'}")

# 武汉的城市 ID（和风天气）
WUHAN_LOCATION_ID = "101200101"

def get_wuhan_weather() -> dict:
    """获取武汉未来三天天气预报（和风天气API）"""
    if not QWEATHER_KEY:
        raise ValueError("QWEATHER_KEY 未设置")

    # 和风天气 3天预报 API
    url = "https://devapi.qweather.com/v7/weather/3d"
    params = {
        "location": WUHAN_LOCATION_ID,
        "key": QWEATHER_KEY,
        "lang": "zh",  # 中文
    }

    try:
        print("🌐 正在获取和风天气数据...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != "200":
            raise Exception(f"和风天气 API 返回错误：{data.get('code')}")

        print(f"✅ 成功获取 {len(data['daily'])} 天天气数据")
        return data

    except Exception as e:
        print(f"❌ 天气获取失败：{e}")
        raise


def format_weather_message(data: dict) -> str:
    """格式化天气消息为 Telegram HTML"""
    now = datetime.now()
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    date_str = f"{now.strftime('%Y-%m-%d')} {weekdays[now.weekday()]}"

    # 构建消息头
    message = f"""🌤 <b>武汉未来三天天气预报</b>
📅 {date_str}

"""

    # 天气图标映射（和风天气代码 → emoji）
    weather_icons = {
        "晴": "☀️", "多云": "🌤", "阴": "☁️", "阵雨": "🌦", "雷阵雨": "⛈",
        "雨": "🌧", "小雨": "🌦", "中雨": "🌧", "大雨": "🌧", "暴雨": "⛈",
        "雪": "❄️", "小雪": "🌨", "中雪": "❄️", "大雪": "❄️",
        "雾": "🌫", "霾": "😷", "扬沙": "💨", "浮尘": "💨",
    }

    # 遍历三天数据
    for day in data["daily"]:
        date = day["fxDate"]  # 日期，如 2026-07-29
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        weekday = weekdays[date_obj.weekday()]

        text_day = day["textDay"]  # 白天天气
        text_night = day["textNight"]  # 夜间天气
        temp_max = day["tempMax"]  # 最高温
        temp_min = day["tempMin"]  # 最低温
        humidity = day["humidity"]  # 湿度
        precip = day["precip"]  # 降水量
        wind_dir = day["windDirDay"]  # 风向
        wind_scale = day["windScaleDay"]  # 风力等级

        # 选择天气图标
        icon = weather_icons.get(text_day, "🌡")

        # 构建单天消息
        message += f"""━━━━━━━━━━━━━━━
📆 <b>{date_obj.strftime('%m月%d日')} {weekday}</b>
{icon} {text_day} → {text_night}
🌡 {temp_min}°C ~ {temp_max}°C
💧 湿度 {humidity}% · 降水 {precip}mm
💨 {wind_dir} {wind_scale}级

"""

    # 添加数据来源
    update_time = data.get("updateTime", "")
    message += f"""━━━━━━━━━━━━━━━
<i>数据来源：和风天气
更新时间：{update_time}
每日 7:30 自动推送</i>"""

    return message

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
    # 获取天气数据
    weather_data = get_wuhan_weather()

    # 格式化消息
    message = format_weather_message(weather_data)

    # 发送到 Telegram
    send_to_telegram(message)
