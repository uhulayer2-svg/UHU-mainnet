from flask import Flask, request, jsonify
from web3 import Web3

app = Flask(__name__)

# --- CONFIG ---
RPC_URL = "http://localhost:80"
# REPLACE WITH YOUR PRIVATE KEY LOCALLY (DO NOT PUSH TO GIT)
FAUCET_PRIVATE_KEY = "YOUR_PRIVATE_KEY_HERE" 
FAUCET_ADDRESS = "0xd7e2446D4eF2C9C824E8eb7dd143ee5215e9409f"
CHAIN_ID = 8844
AMOUNT_UHU = 1000000 

w3 = Web3(Web3.HTTPProvider(RPC_URL))

@app.route('/claim', methods=['POST'])
def claim():
    try:
        data = request.get_json()
        target_address = w3.to_checksum_address(data.get('address'))
        nonce = w3.eth.get_transaction_count(FAUCET_ADDRESS)
        tx = {
            'nonce': nonce, 'to': target_address, 'value': w3.to_wei(AMOUNT_UHU, 'ether'),
            'gas': 21000, 'gasPrice': w3.to_wei('1', 'gwei'), 'chainId': CHAIN_ID
        }
        signed_tx = w3.eth.account.sign_transaction(tx, FAUCET_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return jsonify({"success": True, "message": "1,000,000 UHU Sent!", "tx_hash": tx_hash.hex()})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
