from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# 從環境變數讀取 Discord Webhook URL (稍後會設定)
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
        
        # 判斷訊號類型並加上表情符號
        if '多頭排列' in message or 'Buy' in message or '↑' in message:
            emoji = '🟢'
            color = 3066993  # 綠色
        elif '空頭排列' in message or 'Sell' in message or '↓' in message:
            emoji = '🔴'
            color = 15158332  # 紅色
        else:
            emoji = '⚪'
            color = 3447003  # 藍色
        
        # 建立 Discord 訊息 (使用 Embed 格式,更美觀)
        discord_payload = {
            "username": "鈔人不會飛",
            "avatar_url": "https://i.imgur.com/4M34hi2.png",  # 可換成你的圖示
            "embeds": [{
                "title": f"{emoji} 交易訊號",
                "description": f"```{message}```",
                "color": color,
                "footer": {
                    "text": f"時間: {taiwan_time} UTC"
                }
            }]
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
    """測試用路徑"""
    test_message = "🧪 測試訊號 - 伺服器運作正常!"
    
    discord_payload = {
        "username": "鈔人不會飛",
        "content": test_message
    }
    
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
        return "測試訊息已發送到 Discord!", 200
    else:
        return "錯誤: 未設定 DISCORD_WEBHOOK_URL", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
