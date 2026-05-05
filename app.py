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
        
        # 取得當前時間 (台灣時區)
        now = datetime.utcnow()
        taiwan_time = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # 判斷訊號類型
        # 多頭相關訊號 (排列 + 貫穿) 都會 @everyone
        if '多頭排列' in message or 'Buy' in message or '貫穿↑' in message or '貫穿多頭' in message:
            emoji = '🟢'
            color = 3066993  # 綠色
            mention = '@everyone'  # 標記所有人
        # 空頭相關訊號 (排列 + 貫穿) 都會 @everyone
        elif '空頭排列' in message or 'Sell' in message or '貫穿↓' in message or '貫穿空頭' in message:
            emoji = '🔴'
            color = 15158332  # 紅色
            mention = '@everyone'  # 標記所有人
        else:
            emoji = '⚪'
            color = 3447003  # 藍色
            mention = '@everyone'  # 其他訊號也標記
        
        # 建立 Discord 訊息
        discord_payload = {
            "content": mention,  # @everyone
            "username": "鈔人不會飛",
            "avatar_url": "https://i.imgur.com/4M34hi2.png",
            "embeds": [{
                "title": f"{emoji} 交易訊號",
                "description": f"```{message}```",
                "color": color,
                "footer": {
                    "text": f"時間: {taiwan_time} UTC"
                }
            }],
            "allowed_mentions": {
                "parse": ["everyone"]  # 允許標記 @everyone
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
    test_message = "多頭排列出現 (EMA20>EMA60>EMA240)"
    
    discord_payload = {
        "content": "@everyone",
        "username": "鈔人不會飛",
        "embeds": [{
            "title": "🟢 交易訊號",
            "description": f"```{test_message}```",
            "color": 3066993
        }],
        "allowed_mentions": {
            "parse": ["everyone"]
        }
    }
    
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
        return "測試訊息已發送 (多頭排列 - 會 @everyone)!", 200
    else:
        return "錯誤: 未設定 DISCORD_WEBHOOK_URL", 500

@app.route('/test-cross', methods=['GET'])
def test_cross():
    """測試用路徑 - 模擬貫穿訊號"""
    test_message = "EMA20+EMA60 即時貫穿 EMA240 (多頭)"
    
    discord_payload = {
        "content": "@everyone",
        "username": "鈔人不會飛",
        "embeds": [{
            "title": "🟢 交易訊號",
            "description": f"```{test_message}```",
            "color": 3066993
        }],
        "allowed_mentions": {
            "parse": ["everyone"]
        }
    }
    
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
        return "測試訊息已發送 (貫穿訊號 - 會 @everyone)!", 200
    else:
        return "錯誤: 未設定 DISCORD_WEBHOOK_URL", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
