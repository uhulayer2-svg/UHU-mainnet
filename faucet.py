from flask import Flask, render_template_string, request, jsonify
import requests
import json
import sqlite3
from datetime import datetime, timedelta
from web3 import Web3

app = Flask(__name__)

# --- CONFIG ---
RPC_URL = "http://localhost:80"
# !!! อย่าลืมใส่ Private Key จริงของกระเป๋าที่มีเงิน UHU ในเครื่องหมายคำพูดด้านล่าง !!!
FAUCET_PRIVATE_KEY = "ใส่_PRIVATE_KEY_ของกัปตันตรงนี้"
FAUCET_ADDRESS = "0x2eeb0f207c8cf5fe5f74f50d54572183fdf1087c"
CHAIN_ID = 0x228c
AMOUNT = 1000 * 10**18  # แจก 1,000 UHU
COOLDOWN_HOURS = 24

# Init DB
conn = sqlite3.connect('faucet.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS claims (address TEXT PRIMARY KEY, last_claim TIMESTAMP)')
conn.commit()

w3 = Web3()

def call_rpc(method, params=[]):
    try:
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        response = requests.post(RPC_URL, json=payload)
        return response.json().get('result')
    except:
        return None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>UHU Faucet</title>
    <style>
        body { font-family: 'Inter', sans-serif; background: #0b0f19; color: white; padding: 40px; text-align: center; }
        .card { background: #111827; padding: 40px; border-radius: 20px; max-width: 450px; margin: auto; border: 1px solid #1f2937; }
        h1 { color: #38bdf8; margin-bottom: 10px; }
        input { padding: 15px; width: 90%; margin: 20px 0; border-radius: 8px; border: 1px solid #374151; background: #1f2937; color: white; font-size: 1rem; }
        button { padding: 15px 30px; background: #38bdf8; border: none; border-radius: 8px; color: #0f172a; font-weight: bold; cursor: pointer; width: 100%; font-size: 1.1rem; }
        button:hover { background: #0ea5e9; }
        #message { margin-top: 25px; line-height: 1.5; color: #9ca3af; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🤑 UHU Faucet</h1>
        <p style="color: #9ca3af;">Claim 1,000 UHU for testing purposes!</p>
        <form id="faucet-form">
            <input type="text" id="address" placeholder="Wallet Address (0x...)" required>
            <button type="submit">Claim 1,000 UHU</button>
        </form>
        <div id="message"></div>
    </div>
    <script>
        document.getElementById('faucet-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const addr = document.getElementById('address').value;
            const msg = document.getElementById('message');
            msg.textContent = '⏳ Processing transaction...';
            msg.style.color = '#38bdf8';
            try {
                const res = await fetch('/claim', { 
                    method: 'POST', 
                    headers: {'Content-Type': 'application/json'}, 
                    body: JSON.stringify({address: addr}) 
                });
                const data = await res.json();
                msg.textContent = data.message;
                msg.style.color = data.success ? '#34d399' : '#f87171';
            } catch (err) { 
                msg.textContent = '❌ Error: ' + err; 
                msg.style.color = '#f87171';
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/claim', methods=['POST'])
def claim():
    data = request.json
    user_addr = data.get('address')
    
    if not w3.is_address(user_addr):
        return jsonify({'success': False, 'message': 'Invalid Ethereum address!'})

    cursor.execute("SELECT last_claim FROM claims WHERE address=?", (user_addr,))
    row = cursor.fetchone()
    if row and datetime.now() - datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') < timedelta(hours=COOLDOWN_HOURS):
        return jsonify({'success': False, 'message': '⚠️ Cooldown! You can claim once every 24 hours.'})

    nonce_hex = call_rpc("eth_getTransactionCount", [FAUCET_ADDRESS, "latest"])
    if nonce_hex is None:
        return jsonify({'success': False, 'message': '❌ Node is offline!'})
    
    nonce = int(nonce_hex, 16)
    
    tx = {
        'from': FAUCET_ADDRESS,
        'to': user_addr,
        'value': AMOUNT,
        'gas': 21000,
        'maxFeePerGas': 1000000000, # 1 Gwei
        'maxPriorityFeePerGas': 1000000000,
        'nonce': nonce,
        'chainId': CHAIN_ID,
        'type': 2
    }

    try:
        signed_tx = w3.eth.account.sign_transaction(tx, FAUCET_PRIVATE_KEY)
        tx_hash = call_rpc("eth_sendRawTransaction", [signed_tx.rawTransaction.to_0x_hex()])
        
        if not tx_hash:
            return jsonify({'success': False, 'message': '❌ Node rejected transaction!'})

        cursor.execute("INSERT OR REPLACE INTO claims (address, last_claim) VALUES (?, ?)", 
                       (user_addr, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        return jsonify({'success': True, 'message': f'✅ Success! 1,000 UHU sent.<br>Tx: {tx_hash}'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Faucet Error: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
