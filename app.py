from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

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
        
        # TradingView 可能直接傳文字或 JSON
        message = data.get('message', raw_data) if data else raw_data
        
        # 取得當前時間 (台灣時區 +8)
        from datetime import timedelta
        now = datetime.utcnow() + timedelta(hours=8)
        taiwan_time = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # 判斷訊號類型並設定樣式
        if '多頭排列' in message:
            # 多頭排列訊號
            title = "🚀 多頭排列訊號 🚀"
            description = f"""```
═══════════════════════════
📈 上漲趨勢確認 📈
───────────────────────────
訊號: 多頭排列出現
排列: EMA20 > EMA60 > EMA240
⏰ 時間: {taiwan_time}
═══════════════════════════
```"""
            color = 3066993  # 綠色
            thumbnail = "https://i.imgur.com/qxz0g5h.png"  # 上漲圖示
            
        elif '空頭排列' in message:
            # 空頭排列訊號
            title = "📉 空頭排列訊號 📉"
            description = f"""```
═══════════════════════════
📉 下跌趨勢確認 📉
───────────────────────────
訊號: 空頭排列出現
排列: EMA20 < EMA60 < EMA240
⏰ 時間: {taiwan_time}
═══════════════════════════
```"""
            color = 15158332  # 紅色
            thumbnail = "https://i.imgur.com/3xqJGfP.png"  # 下跌圖示
            
        elif '貫穿多頭' in message or '貫穿↑' in message or 'Buy' in message:
            # 多頭貫穿訊號
            title = "⚡ 多頭貫穿訊號 ⚡"
            description = f"""```
═══════════════════════════
⚡📈 突破上漲訊號 📈⚡
───────────────────────────
訊號: EMA20+60 貫穿 EMA240
方向: 向上突破 ↑↑↑
⏰ 時間: {taiwan_time}
═══════════════════════════
```"""
            color = 3066993  # 綠色
            thumbnail = "https://i.imgur.com/qxz0g5h.png"  # 上漲圖示
            
        elif '貫穿空頭' in message or '貫穿↓' in message or 'Sell' in message:
            # 空頭貫穿訊號
            title = "⚡ 空頭貫穿訊號 ⚡"
            description = f"""```
═══════════════════════════
⚡📉 突破下跌訊號 📉⚡
───────────────────────────
訊號: EMA20+60 貫穿 EMA240
方向: 向下突破 ↓↓↓
⏰ 時間: {taiwan_time}
═══════════════════════════
```"""
            color = 15158332  # 紅色
            thumbnail = "https://i.imgur.com/3xqJGfP.png"  # 下跌圖示
            
        else:
            # 其他訊號
            title = "📊 交易訊號"
            description = f"""```
═══════════════════════════
{message}
⏰ 時間: {taiwan_time}
═══════════════════════════
```"""
            color = 3447003  # 藍色
            thumbnail = None
        
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
                    "text": "鈔人不會飛交易系統",
                    "icon_url": "https://i.imgur.com/4M34hi2.png"
                }
            }],
            "allowed_mentions": {
                "parse": ["everyone"]
            }
        }
        
        # 如果有縮圖,加入
        if thumbnail:
            discord_payload["embeds"][0]["thumbnail"] = {"url": thumbnail}
        
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
訊號: 多頭排列出現
排列: EMA20 > EMA60 > EMA240
⏰ 時間: {taiwan_time}
═══════════════════════════
```""",
            "color": 3066993,
            "thumbnail": {"url": "https://i.imgur.com/qxz0g5h.png"},
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "鈔人不會飛交易系統",
                "icon_url": "https://i.imgur.com/4M34hi2.png"
            }
        }],
        "allowed_mentions": {
            "parse": ["everyone"]
        }
    }
    
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
        return "測試訊息已發送 (多頭排列 📈)!", 200
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
訊號: 空頭排列出現
排列: EMA20 < EMA60 < EMA240
⏰ 時間: {taiwan_time}
═══════════════════════════
```""",
            "color": 15158332,
            "thumbnail": {"url": "https://i.imgur.com/3xqJGfP.png"},
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "鈔人不會飛交易系統",
                "icon_url": "https://i.imgur.com/4M34hi2.png"
            }
        }],
        "allowed_mentions": {
            "parse": ["everyone"]
        }
    }
    
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
        return "測試訊息已發送 (空頭排列 📉)!", 200
    else:
        return "錯誤: 未設定 DISCORD_WEBHOOK_URL", 500

@app.route('/test-cross-bull', methods=['GET'])
def test_cross_bull():
    """測試用路徑 - 模擬多頭貫穿訊號"""
    from datetime import timedelta
    now = datetime.utcnow() + timedelta(hours=8)
    taiwan_time = now.strftime('%Y-%m-%d %H:%M:%S')
    
    discord_payload = {
        "content": "@everyone",
        "username": "鈔人不會飛",
        "avatar_url": "https://i.imgur.com/4M34hi2.png",
        "embeds": [{
            "title": "⚡ 多頭貫穿訊號 ⚡",
            "description": f"""```
═══════════════════════════
⚡📈 突破上漲訊號 📈⚡
───────────────────────────
訊號: EMA20+60 貫穿 EMA240
方向: 向上突破 ↑↑↑
⏰ 時間: {taiwan_time}
═══════════════════════════
```""",
            "color": 3066993,
            "thumbnail": {"url": "https://i.imgur.com/qxz0g5h.png"},
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "鈔人不會飛交易系統",
                "icon_url": "https://i.imgur.com/4M34hi2.png"
            }
        }],
        "allowed_mentions": {
            "parse": ["everyone"]
        }
    }
    
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
        return "測試訊息已發送 (多頭貫穿 ⚡📈)!", 200
    else:
        return "錯誤: 未設定 DISCORD_WEBHOOK_URL", 500

@app.route('/test-cross-bear', methods=['GET'])
def test_cross_bear():
    """測試用路徑 - 模擬空頭貫穿訊號"""
    from datetime import timedelta
    now = datetime.utcnow() + timedelta(hours=8)
    taiwan_time = now.strftime('%Y-%m-%d %H:%M:%S')
    
    discord_payload = {
        "content": "@everyone",
        "username": "鈔人不會飛",
        "avatar_url": "https://i.imgur.com/4M34hi2.png",
        "embeds": [{
            "title": "⚡ 空頭貫穿訊號 ⚡",
            "description": f"""```
═══════════════════════════
⚡📉 突破下跌訊號 📉⚡
───────────────────────────
訊號: EMA20+60 貫穿 EMA240
方向: 向下突破 ↓↓↓
⏰ 時間: {taiwan_time}
═══════════════════════════
```""",
            "color": 15158332,
            "thumbnail": {"url": "https://i.imgur.com/3xqJGfP.png"},
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "鈔人不會飛交易系統",
                "icon_url": "https://i.imgur.com/4M34hi2.png"
            }
        }],
        "allowed_mentions": {
            "parse": ["everyone"]
        }
    }
    
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
        return "測試訊息已發送 (空頭貫穿 ⚡📉)!", 200
    else:
        return "錯誤: 未設定 DISCORD_WEBHOOK_URL", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
