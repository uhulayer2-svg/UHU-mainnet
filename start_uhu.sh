#!/bin/bash
echo "🛠️  Igniting UHU Pulse Ecosystem..."

# หยุด Process เก่าทั้งหมดให้เกลี้ยง
sudo fuser -k 80/tcp 8080/tcp 8081/tcp 2>/dev/null
pkill -f ngrok

# 1. Start Rust Node
nohup sudo ./target/debug/uhu-rust-node > node.log 2>&1 &
echo "✅ L1 Node Online (Port 80)"

# 2. Start Explorer
nohup ./venv/bin/python3 dashboard.py > dashboard.log 2>&1 &
echo "✅ Explorer Online (Port 8080)"

# 3. Start Faucet
nohup ./venv/bin/python3 faucet.py > faucet.log 2>&1 &
echo "✅ Faucet Online (Port 8081)"

# 4. Start ngrok
nohup ngrok http 80 > ngrok.log 2>&1 &
sleep 5
echo "✅ ngrok Tunneling Active"

echo "--------------------------------------"
echo "🛰️  ALL SYSTEMS ONLINE & STABLE!"
curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'
echo "--------------------------------------"
