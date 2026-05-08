from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime
import json

app = Flask(__name__)

# 從環境變數讀取 Discord Webhook URL
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')

@app.route('/', methods=['GET'])
def home():
    return """
    <h1>🚀 鈔人不會飛 - TradingView to Discord Webhook</h1>
    <p>伺服器運行中...</p>
    <p>請在 TradingView 警報中使用此 URL + /alert</p>
    """, 200

@app.route('/alert', methods=['POST'])
def tradingview_alert():
    try:
        # 取得 TradingView 傳來的資料
        data = request.get_json() if request.is_json else {}
        raw_data = request.data.decode('utf-8') if request.data else ''
        
        # 嘗試解析 JSON 格式的訊息
        ticker = "未知商品"
        price = ""
        interval = ""
        exchange = ""
        message_text = ""
        
        if data:
            # 如果是 JSON 格式
            ticker = data.get('ticker', '未知商品')
            price = data.get('price', data.get('close', ''))
            interval = data.get('interval', '')
            exchange = data.get('exchange', '')
            message_text = data.get('message', '')
        else:
            # 如果是純文字,嘗試解析
            message_text = raw_data
            
            # 簡單解析 (如果訊息包含這些資訊)
            if '{{ticker}}' not in message_text:
                # 如果訊息已經被 TradingView 替換過變數
                lines = message_text.split('\n')
                for line in lines:
                    if 'ticker:' in line.lower():
                        ticker = line.split(':', 1)[1].strip()
                    elif 'price:' in line.lower() or '價格:' in line:
                        price = line.split(':', 1)[1].strip()
        
        # 取得當前時間 (台灣時區 +8)
        from datetime import timedelta
        now = datetime.utcnow() + timedelta(hours=8)
        taiwan_time = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # 判斷訊號類型並設定樣式
        if '多頭排列' in message_text:
            # 多頭排列訊號
            title = "🚀 多頭排列訊號 🚀"
            description = f"""```
═══════════════════════════
📈 上漲趨勢確認 📈
───────────────────────────
🏷️ 商品: {ticker}
💰 價格: {price if price else '請查看圖表'}
📊 週期: {interval if interval else '請查看圖表'}
───────────────────────────
訊號: 多頭排列出現
排列: EMA20 > EMA60 > EMA240
⏰ 時間: {taiwan_time}
═══════════════════════════
```"""
            color = 3066993  # 綠色
            
        elif '空頭排列' in message_text:
            # 空頭排列訊號
            title = "📉 空頭排列訊號 📉"
            description = f"""```
═══════════════════════════
📉 下跌趨勢確認 📉
───────────────────────────
🏷️ 商品: {ticker}
💰 價格: {price if price else '請查看圖表'}
📊 週期: {interval if interval else '請查看圖表'}
───────────────────────────
訊號: 空頭排列出現
排列: EMA20 < EMA60 < EMA240
⏰ 時間: {taiwan_time}
═══════════════════════════
```"""
            color = 15158332  # 紅色
            
        elif '貫穿多頭' in message_text or '貫穿↑' in message_text or 'Buy' in message_text:
            # 多頭貫穿訊號
            title = "⚡ 多頭貫穿訊號 ⚡"
            description = f"""```
═══════════════════════════
⚡📈 突破上漲訊號 📈⚡
───────────────────────────
🏷️ 商品: {ticker}
💰 價格: {price if price else '請查看圖表'}
📊 週期: {interval if interval else '請查看圖表'}
───────────────────────────
訊號: EMA20+60 貫穿 EMA240
方向: 向上突破 ↑↑↑
⏰ 時間: {taiwan_time}
═══════════════════════════
```"""
            color = 3066993  # 綠色
            
        elif '貫穿空頭' in message_text or '貫穿↓' in message_text or 'Sell' in message_text:
            # 空頭貫穿訊號
            title = "⚡ 空頭貫穿訊號 ⚡"
            description = f"""```
═══════════════════════════
⚡📉 突破下跌訊號 📉⚡
───────────────────────────
🏷️ 商品: {ticker}
💰 價格: {price if price else '請查看圖表'}
📊 週期: {interval if interval else '請查看圖表'}
───────────────────────────
訊號: EMA20+60 貫穿 EMA240
方向: 向下突破 ↓↓↓
⏰ 時間: {taiwan_time}
═══════════════════════════
```"""
            color = 15158332  # 紅色
            
        else:
            # 其他訊號
            title = "📊 交易訊號"
            description = f"""```
═══════════════════════════
🏷️ 商品: {ticker}
💰 價格: {price if price else '請查看圖表'}
───────────────────────────
{message_text}
⏰ 時間: {taiwan_time}
═══════════════════════════
```"""
            color = 3447003  # 藍色
        
        # 建立 Discord 訊息 (使用 Embed 格式)
        discord_payload = {
            "content": "@everyone",  # 標記所有人
            "username": "鈔人不會飛",
            "avatar_url": "https://i.imgur.com/4M34hi2.png",
            "embeds": [{
                "title": title,
                "description": description,
                "color": color,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": f"鈔人不會飛交易系統 | {exchange if exchange else '交易所'}",
                    "icon_url": "https://i.imgur.com/4M34hi2.png"
                }
            }],
            "allowed_mentions": {
                "parse": ["everyone"]
            }
        }
        
        # 發送到 Discord
        if DISCORD_WEBHOOK_URL:
            response = requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
            
            if response.status_code == 204:
                return jsonify({"status": "success", "message": "已發送到 Discord"}), 200
            else:
                return jsonify({"status": "error", "message": f"Discord 錯誤: {response.status_code}"}), 500
        else:
            return jsonify({"status": "error", "message": "未設定 DISCORD_WEBHOOK_URL"}), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    """測試用路徑 - 模擬多頭排列訊號"""
    from datetime import timedelta
    now = datetime.utcnow() + timedelta(hours=8)
    taiwan_time = now.strftime('%Y-%m-%d %H:%M:%S')
    
    discord_payload = {
        "content": "@everyone",
        "username": "鈔人不會飛",
        "avatar_url": "https://i.imgur.com/4M34hi2.png",
        "embeds": [{
            "title": "🚀 多頭排列訊號 🚀",
            "description": f"""```
═══════════════════════════
📈 上漲趨勢確認 📈
───────────────────────────
🏷️ 商品: BTCUSD (測試)
💰 價格: 98,234.50
📊 週期: 1H
───────────────────────────
訊號: 多頭排列出現
排列: EMA20 > EMA60 > EMA240
⏰ 時間: {taiwan_time}
═══════════════════════════
```""",
            "color": 3066993,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "鈔人不會飛交易系統 | BINANCE",
                "icon_url": "https://i.imgur.com/4M34hi2.png"
            }
        }],
        "allowed_mentions": {
            "parse": ["everyone"]
        }
    }
    
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
        return "測試訊息已發送 (含商品資訊)!", 200
    else:
        return "錯誤: 未設定 DISCORD_WEBHOOK_URL", 500

@app.route('/test-bear', methods=['GET'])
def test_bear():
    """測試用路徑 - 模擬空頭排列訊號"""
    from datetime import timedelta
    now = datetime.utcnow() + timedelta(hours=8)
    taiwan_time = now.strftime('%Y-%m-%d %H:%M:%S')
    
    discord_payload = {
        "content": "@everyone",
        "username": "鈔人不會飛",
        "avatar_url": "https://i.imgur.com/4M34hi2.png",
        "embeds": [{
            "title": "📉 空頭排列訊號 📉",
            "description": f"""```
═══════════════════════════
📉 下跌趨勢確認 📉
───────────────────────────
🏷️ 商品: 台積電 2330
💰 價格: 1,055
📊 週期: 日線
───────────────────────────
訊號: 空頭排列出現
排列: EMA20 < EMA60 < EMA240
⏰ 時間: {taiwan_time}
═══════════════════════════
```""",
            "color": 15158332,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "鈔人不會飛交易系統 | TWSE",
                "icon_url": "https://i.imgur.com/4M34hi2.png"
            }
        }],
        "allowed_mentions": {
            "parse": ["everyone"]
        }
    }
    
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
        return "測試訊息已發送 (含商品資訊)!", 200
    else:
        return "錯誤: 未設定 DISCORD_WEBHOOK_URL", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
