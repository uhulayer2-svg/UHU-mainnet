from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

# --- ⚙️ CONFIG ---
GENESIS_PRICE = 0.000002
COINGECKO_API = "https://api.coingecko.com/api/v3"

# --- 🧭 ROUTES ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/projects')
def projects(): return render_template('projects.html')

@app.route('/roadmap')
def roadmap(): return render_template('roadmap.html')

@app.route('/tokenomics')
def tokenomics(): return render_template('tokenomics.html')

@app.route('/legal-ai')
def legal_ai(): return render_template('legal_ai.html')

@app.route('/whitepaper')
def whitepaper(): return render_template('whitepaper.html')

@app.route('/scan')
def scan(): return render_template('scan.html')

@app.route('/trading-bot')
def trading_bot(): return render_template('trading_bot.html')

# --- 📊 API DATA SYNC ---
@app.route('/api/market-real')
def api_market():
    uhu_tokens = [
        {"id": "uhu-pulse", "symbol": "pulse", "name": "UHU+ PULSE", "image": "/static/img/logouhu.png", "current_price": GENESIS_PRICE, "price_change_percentage_24h": 5.42, "is_uhu": True},
        {"id": "uhu-lithium", "symbol": "lihu", "name": "LIHU (Lithium)", "image": "https://cdn-icons-png.flaticon.com/512/2441/2441113.png", "current_price": 1.25, "price_change_percentage_24h": 0.12, "is_uhu": True},
        {"id": "uhu-gold", "symbol": "guhu", "name": "GUHU (Gold)", "image": "https://cdn-icons-png.flaticon.com/512/2489/2489745.png", "current_price": 2350.50, "price_change_percentage_24h": -0.05, "is_uhu": True}
    ]
    try:
        res = requests.get(f"{COINGECKO_API}/coins/markets", params={"vs_currency": "usd", "per_page": 10}, timeout=5)
        return jsonify(uhu_tokens + res.json())
    except: return jsonify(uhu_tokens)

@app.route('/api/bot-status')
def bot_status():
    return jsonify({"status": "Active", "strategy": "Volatility Engine v2", "balance": "12,450.60", "active_trades": 3, "pnl": "+4.25%"})

@app.route('/api/ai-query', methods=['POST'])
def ai_query():
    user_msg = request.json.get('message', '').lower()
    return jsonify({"answer": "รับทราบครับกัปตัน! ระบบกำลังประมวลผลข้อมูลผ่าน Neural Node..."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)