# 鈔人不會飛 - TradingView to Discord Webhook

這是一個將 TradingView 警報轉發到 Discord 的中繼伺服器。

## 部署步驟

### 1. 上傳到 GitHub
- 在 GitHub 建立新 repository
- 上傳這三個檔案: app.py, requirements.txt, Procfile

### 2. 部署到 Render
1. 前往 https://render.com (使用 GitHub 帳號註冊/登入)
2. 點擊 "New +" → "Web Service"
3. 連接你的 GitHub repository
4. 設定:
   - Name: tradingview-discord-webhook
   - Environment: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn app:app
5. 在 "Environment Variables" 新增:
   - Key: DISCORD_WEBHOOK_URL
   - Value: (你的 Discord Webhook URL)
6. 選擇 Free 方案
7. 點擊 "Create Web Service"

### 3. 在 TradingView 設定警報
1. 開啟 TradingView 圖表
2. 點擊警報圖示
3. 選擇你的指標「鈔人不會飛」
4. 在 Webhook URL 填入: https://你的服務名稱.onrender.com/alert
5. 訊息格式填入警報訊息
6. 儲存

## 測試
訪問 https://你的服務名稱.onrender.com/test 測試是否正常運作
