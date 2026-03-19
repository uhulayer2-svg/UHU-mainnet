from flask import Flask, render_template, jsonify, request
import requests
import random

app = Flask(__name__)

# ==========================================
# 💎 CONFIGURATION
# ==========================================
GENESIS_PRICE = 0.000002
COINGECKO_API = "https://api.coingecko.com/api/v3"

# ==========================================
# 🧭 NAVIGATION ROUTES
# ==========================================
@app.route('/')
def index(): return render_template('index.html')

@app.route('/coin/<id>')
def coin_page(id): return render_template('coin_detail.html', coin_id=id)

@app.route('/why-uhu')
def why_uhu(): return render_template('why_uhu.html')

@app.route('/projects')
def projects(): return render_template('projects.html')

@app.route('/whitepaper')
def whitepaper(): return render_template('whitepaper.html')

@app.route('/scan')
def scan(): return render_template('scan.html')

@app.route('/get-uhu')
def get_uhu(): return render_template('get_uhu.html')

@app.route('/trading-bot')
def trading_bot(): return render_template('trading_bot.html')

# ==========================================
# 📊 API SYSTEM (The Data Pulse)
# ==========================================

@app.route('/api/market-real')
def api_market():
    """ดึงข้อมูลเหรียญโลก 20 อันดับ + UHU+ 3 พี่น้อง"""
    try:
        url = f"{COINGECKO_API}/coins/markets"
        params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 20, "page": 1}
        response = requests.get(url, params=params, timeout=5)
        global_data = response.json()
        
        uhu_tokens = [
            {"id": "uhu-pulse", "symbol": "pulse", "name": "UHU+ PULSE", "image": "/static/img/logouhu.png", "current_price": GENESIS_PRICE, "market_cap": "Genesis", "price_change_percentage_24h": 5.42, "is_uhu": True},
            {"id": "uhu-lithium", "symbol": "lihu", "name": "LIHU (Lithium)", "image": "https://cdn-icons-png.flaticon.com/512/2441/2441113.png", "current_price": 1.25, "market_cap": "RWA Backed", "price_change_percentage_24h": 0.12, "is_uhu": True},
            {"id": "uhu-gold", "symbol": "guhu", "name": "GUHU (Gold)", "image": "https://cdn-icons-png.flaticon.com/512/2489/2489745.png", "current_price": 2350.50, "market_cap": "Gold Backed", "price_change_percentage_24h": -0.05, "is_uhu": True}
        ]
        return jsonify(uhu_tokens + global_data)
    except:
        return jsonify([{"id": "uhu-pulse", "name": "UHU+ PULSE", "current_price": GENESIS_PRICE, "is_uhu": True}])

@app.route('/api/coin-details/<id>')
def api_coin_details(id):
    """ส่งข้อมูลรายละเอียดเหรียญรายตัว"""
    uhu_db = {
        "uhu-pulse": {
            "name": "UHU+ PULSE", "symbol": "PULSE", "price": GENESIS_PRICE, "image": "/static/img/logouhu.png",
            "desc": "The core governance token of UHU+ Layer 1. Built with Rust for maximum security.", "market_cap": "Genesis Phase", "supply": "1,000,000,000"
        },
        "uhu-lithium": {
            "name": "LIHU (Lithium)", "symbol": "LIHU", "price": 1.25, "image": "https://cdn-icons-png.flaticon.com/512/2441/2441113.png",
            "desc": "Asset-backed token representing physical lithium reserves.", "market_cap": "RWA Backed", "supply": "Audit Defined"
        },
        "uhu-gold": {
            "name": "GUHU (Gold)", "symbol": "GUHU", "price": 2350.50, "image": "https://cdn-icons-png.flaticon.com/512/2489/2489745.png",
            "desc": "Digital gold token backed 1:1 by physical bullion.", "market_cap": "Gold Backed", "supply": "Fully Audited"
        }
    }
    if id in uhu_db: return jsonify(uhu_db[id])

    try:
        res = requests.get(f"{COINGECKO_API}/coins/{id}", timeout=5)
        d = res.json()
        return jsonify({
            "name": d.get('name'), "symbol": d.get('symbol', '').upper(),
            "price": d.get('market_data', {}).get('current_price', {}).get('usd'),
            "image": d.get('image', {}).get('large'), 
            "desc": d.get('description', {}).get('en', '')[:600] + "...",
            "market_cap": d.get('market_data', {}).get('market_cap', {}).get('usd'),
            "supply": d.get('market_data', {}).get('total_supply')
        })
    except: return jsonify({"error": "Data Sync Offline"}), 500

@app.route('/api/ai-query', methods=['POST'])
def api_ai_query():
    """ระบบหลังบ้านของน้องกุ้ง (Nong Kung)"""
    data = request.json
    msg = data.get('message', '').lower()
    if any(x in msg for x in ["สวัสดี", "hello", "hi"]):
        ans = "สวัสดีครับกัปตัน! น้องกุ้ง (Nong Kung) พร้อมรับใช้ครับ! ถามเรื่อง Projects หรือราคาได้เลยครับ 🦐"
    elif "ราคา" in msg or "price" in msg:
        ans = f"ราคา Genesis ของ UHU+ PULSE อยู่ที่ ${GENESIS_PRICE} ครับ!"
    else:
        ans = "น้องกุ้งกำลังสแกนหาคำตอบให้ครับ กัปตันถามเรื่องระบบ Rust หรือวิธีเชื่อมต่อกระเป๋าได้นะ!"
    return jsonify({"answer": ans})

if __name__ == '__main__':
    app.run(debug=True, port=5000)