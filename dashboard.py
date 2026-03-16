from flask import Flask, render_template_string
import requests
import json

app = Flask(__name__)

def call_rpc(method, params=[]):
    try:
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        response = requests.post("http://localhost", json=payload)
        return response.json().get('result')
    except Exception as e:
        return None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>UHU Pulse Explorer</title>
    <meta http-equiv="refresh" content="3">
    <style>
        body { font-family: 'Inter', -apple-system, sans-serif; background: #0b0f19; color: #e5e7eb; padding: 40px; }
        .container { max-width: 1000px; margin: 0 auto; }
        .card { background: #111827; padding: 24px; border-radius: 16px; border: 1px solid #1f2937; margin-bottom: 24px; }
        h1 { color: #38bdf8; display: flex; align-items: center; gap: 10px; }
        .stat-value { font-size: 2.5em; font-weight: 800; color: #f9fafb; margin-top: 8px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th { text-align: left; padding: 12px; color: #9ca3af; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #1f2937; }
        td { padding: 16px 12px; border-bottom: 1px solid #111827; font-size: 0.9rem; }
        .hash { color: #38bdf8; font-family: monospace; }
        .badge { background: #064e3b; color: #34d399; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
        .amount { font-weight: 600; color: #fbbf24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛰️ UHU Pulse Explorer</h1>
        <div class="card">
            <div style="color: #9ca3af; font-size: 0.875rem;">Network Height (Current Block)</div>
            <div class="stat-value">{{ block_number }}</div>
        </div>
        <div class="card">
            <h3 style="margin-top: 0;">Recent Transactions</h3>
            <table>
                <thead>
                    <tr>
                        <th>Block</th>
                        <th>Hash</th>
                        <th>From</th>
                        <th>To</th>
                        <th>Amount</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for tx in txs %}
                    <tr>
                        <td>#{{ tx.block }}</td>
                        <td class="hash">{{ tx.hash[:12] }}...</td>
                        <td>{{ tx.from[:10] }}...</td>
                        <td>
                            {% if tx.to %}
                                {{ tx.to[:10] }}...
                            {% else %}
                                <span style="color: #a855f7;">Contract Creation</span>
                            {% endif %}
                        </td>
                        <td class="amount">{{ tx.amount }} UHU</td>
                        <td><span class="badge">Confirmed</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <div style="text-align: center; color: #4b5563; font-size: 0.8rem;">Auto-syncing with node every 3 seconds...</div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    block_hex = call_rpc("eth_blockNumber")
    block_num = int(block_hex, 16) if block_hex else 1000
    
    recent_txs = []
    # ดึง 5 บล็อกล่าสุด
    for i in range(block_num, max(block_num - 5, 1000), -1):
        block_data = call_rpc("eth_getBlockByNumber", [hex(i), True])
        if block_data and 'transactions' in block_data:
            for tx in block_data['transactions']:
                amount_wei = int(tx.get('value', '0x0'), 16)
                amount_uhu = amount_wei / 10**18
                recent_txs.append({
                    'block': i,
                    'hash': tx.get('hash', '0x'),
                    'from': tx.get('from', '0x'),
                    'to': tx.get('to'),
                    'amount': f"{amount_uhu:,.2f}"
                })
    
    return render_template_string(HTML_TEMPLATE, block_number=block_num, txs=recent_txs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
