# 💎 UHU Pulse Sovereign L1

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Rust](https://img.shields.io/badge/Rust-1.80+-000000.svg?logo=rust)](https://www.rust-lang.org)
[![Reth](https://img.shields.io/badge/Architecture-Reth_ExEx-FF9900.svg)](https://reth.rs)
[![Status: Alpha](https://img.shields.io/badge/Status-Alpha_Prototype-blue.svg)](https://github.com/uhulayer2-svg/UHU-mainnet)

**Official UHU Pulse Layer 1** — Sovereign L1 ที่ผสาน **Neural Pulse AI** + **Real World Assets (RWA)** บนสถาปัตยกรรม Reth + ExEx

🌐 **Dashboard**: [uhu-mainnet.vercel.app](https://uhu-mainnet.vercel.app)  
🔍 **Explorer**: http://34.170.14.90:8080 (temporary)  
📡 **RPC**: https://nonprovidently-instigative-deloris.ngrok-free.dev (กำลังย้ายไป rpc.uhu-pulse.com ด้วย Cloudflare Tunnel)

---

## 🧭 The Truthful Status (Alpha Prototype)

**ตอนนี้ (Mar 2026)**:  
UHU Pulse ยังอยู่ในระยะ **Alpha Prototype** — เป็น Mock RPC node เขียนด้วย Rust + sled DB + Python ecosystem tools

- รองรับ native transfer ได้จริง  
- ยังไม่มี EVM execution เต็มรูปแบบ  
- Single node (ยังไม่มี P2P / consensus)  
- TPS: **Target Architecture 85,000+** (ยังไม่ใช่ production)

**เรากำลัง migrate ไป Reth Architecture** ด้วย ExEx เพื่อให้ได้:
- Full EVM + Smart Contract (Solidity/Vyper)  
- Production-grade P2P + Mempool  
- Custom Neural Pulse AI Precompiles  
- RWA Standard (ERC-3643 / T-REX)

**ทุกอย่างโปร่งใส 100%** — เราจะไม่ overclaim จนกว่าจะถึง production mainnet

---

## 🏗️ Architecture (Current → Future)

```mermaid
graph TD
    subgraph Current["Current Alpha (Prototype)"]
        A[Rust Mock RPC + sled DB]
        B[Python Dashboard + Faucet]
        C[Explorer uhu-scan]
    end

    subgraph Future["Future: Reth Sovereign L1 (2026 Master Plan)"]
        D[Reth Base Node<br/>P2P + Mempool + Full revm]
        E[ExEx: Custom Execution Extensions]
        F[Neural Pulse AI Precompiles<br/>Real-time Algorithmic Trading]
        G[RWA Engine<br/>ERC-3643 Tokenized Assets<br/>Lithium & Gold Deeds]
        H[Cloudflare Tunnel + Domain<br/>rpc.uhu-pulse.com]
    end

    Current -->|Migrate Week 2-3| Future
    style Future fill:#FF9900,stroke:#333,stroke-width:2px
