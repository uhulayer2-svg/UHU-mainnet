#!/bin/bash

NODE_BIN="./target/debug/uhu-rust-node"
LOG_FILE="node.log"

case "$1" in
    start)
        echo "🚀 กำลังสตาร์ทยานแม่ UHU Chain..."
        sudo fuser -k 80/tcp > /dev/null 2>&1
        sudo nohup $NODE_BIN > $LOG_FILE 2>&1 &
        echo "✅ ออนไลน์เรียบร้อย! (ดู Log ได้ที่ ./uhu.sh logs)"
        ;;
    stop)
        echo "🛑 กำลังสั่งพักเครื่อง..."
        sudo fuser -k 80/tcp > /dev/null 2>&1
        sudo pkill uhu-rust-node > /dev/null 2>&1
        echo "💤 ยานแม่ลงจอดพักผ่อนแล้วครับ"
        ;;
    status)
        if sudo fuser 80/tcp > /dev/null 2>&1; then
            echo "🟢 สถานะ: ONLINE (รันอยู่บนพอร์ต 80)"
        else
            echo "🔴 สถานะ: OFFLINE"
        fi
        ;;
    logs)
        echo "📜 ขอดูบันทึกการเดินทางล่าสุด (กด Ctrl+C เพื่อออก):"
        tail -f $LOG_FILE
        ;;
    clean)
        echo "🧹 กำลังล้างฐานข้อมูลและประวัติทั้งหมด..."
        sudo fuser -k 80/tcp > /dev/null 2>&1
        sudo rm -rf uhu_db node.log
        echo "✨ สะอาดเอี่ยมเหมือนใหม่ครับกัปตัน!"
        ;;
    *)
        echo "❓ วิธีใช้: ./uhu.sh {start|stop|status|logs|clean}"
        ;;
esac
