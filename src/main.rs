use alloy_primitives::{Address, U256, B256, keccak256, TxKind};
use alloy::consensus::{TxEnvelope, Transaction};
use alloy_eips::eip2718::Decodable2718;
use jsonrpsee::core::async_trait;
use jsonrpsee::proc_macros::rpc;
use jsonrpsee::server::ServerBuilder;
use jsonrpsee::types::error::ErrorObject;
use serde::{Serialize, Deserialize};
use serde_json::json;
use std::sync::Arc;
use tokio::sync::RwLock;
use std::net::SocketAddr;

#[rpc(server)]
pub trait UhuRpc {
    #[method(name = "eth_chainId")] fn chain_id(&self) -> Result<String, ErrorObject<'static>>;
    #[method(name = "net_version")] fn net_version(&self) -> Result<String, ErrorObject<'static>>;
    #[method(name = "eth_blockNumber")] async fn block_number(&self) -> Result<String, ErrorObject<'static>>;
    #[method(name = "eth_getBalance")] async fn get_balance(&self, addr: Address, _tag: String) -> Result<String, ErrorObject<'static>>;
    #[method(name = "eth_getTransactionCount")] async fn get_transaction_count(&self, addr: Address, _tag: String) -> Result<String, ErrorObject<'static>>;
    #[method(name = "eth_sendRawTransaction")] async fn send_raw_transaction(&self, hex_raw: String) -> Result<String, ErrorObject<'static>>;
    #[method(name = "eth_getTransactionReceipt")] async fn get_transaction_receipt(&self, hash: B256) -> Result<Option<serde_json::Value>, ErrorObject<'static>>;
    #[method(name = "eth_getBlockByNumber")] async fn get_block_by_number(&self, num: String, full: bool) -> Result<Option<serde_json::Value>, ErrorObject<'static>>;
    #[method(name = "eth_estimateGas")] fn estimate_gas(&self) -> Result<String, ErrorObject<'static>>;
    #[method(name = "eth_gasPrice")] fn gas_price(&self) -> Result<String, ErrorObject<'static>>;
    #[method(name = "eth_maxPriorityFeePerGas")] fn max_priority_fee(&self) -> Result<String, ErrorObject<'static>>;
    #[method(name = "eth_call")] async fn eth_call(&self, tx: serde_json::Value, block: String) -> Result<String, ErrorObject<'static>>;
}

#[derive(Serialize, Deserialize, Clone)]
struct TransactionInfo { 
    from: Address, to: Option<Address>, contract_address: Option<Address>,
    amount: U256, block_number: u64, hash: B256, nonce: u64, gas_limit: u64,
    effective_gas_price: U256, max_fee: U256, priority_fee: U256, base_fee: U256
}

struct UhuNode { db: sled::Db, state: Arc<RwLock<()>> }

impl UhuNode {
    fn get_u256(&self, tree: &str, key: &[u8]) -> U256 {
        self.db.open_tree(tree).unwrap().get(key).unwrap().map(|v| U256::from_be_slice(&v)).unwrap_or(U256::ZERO)
    }
    fn set_u256(&self, tree: &str, key: &[u8], val: U256) {
        self.db.open_tree(tree).unwrap().insert(key, &val.to_be_bytes::<32>()).unwrap();
    }
}

#[async_trait]
impl UhuRpcServer for UhuNode {
    fn chain_id(&self) -> Result<String, ErrorObject<'static>> { Ok("0x228c".to_string()) }
    fn net_version(&self) -> Result<String, ErrorObject<'static>> { Ok("8844".to_string()) }

    async fn block_number(&self) -> Result<String, ErrorObject<'static>> {
        let h = self.db.get(b"bh").unwrap().map(|v| u64::from_be_bytes(v.as_ref().try_into().unwrap())).unwrap_or(1000);
        Ok(format!("0x{:x}", h))
    }

    async fn get_balance(&self, addr: Address, _tag: String) -> Result<String, ErrorObject<'static>> {
        Ok(format!("0x{:x}", self.get_u256("bal", addr.as_slice())))
    }

    async fn get_transaction_count(&self, addr: Address, _tag: String) -> Result<String, ErrorObject<'static>> {
        let n = self.db.open_tree("non").unwrap().get(addr.as_slice()).unwrap().map(|v| u64::from_be_bytes(v.as_ref().try_into().unwrap())).unwrap_or(0);
        Ok(format!("0x{:x}", n))
    }

    async fn send_raw_transaction(&self, hex_raw: String) -> Result<String, ErrorObject<'static>> {
        let _lock = self.state.write().await;
        let bytes = hex::decode(hex_raw.trim_start_matches("0x")).map_err(|_| ErrorObject::owned(-32000, "Hex err", None::<()>))?;
        let tx_env = TxEnvelope::decode_2718(&mut &bytes[..]).map_err(|_| ErrorObject::owned(-32000, "Dec err", None::<()>))?;
        let sender = tx_env.recover_signer().map_err(|_| ErrorObject::owned(-32000, "Sig err", None::<()>))?;
        
        let non_tree = self.db.open_tree("non").unwrap();
        let current_nonce = non_tree.get(sender.as_slice()).unwrap().map(|v| u64::from_be_bytes(v.as_ref().try_into().unwrap())).unwrap_or(0);
        
        if tx_env.nonce() != current_nonce {
            let msg = if tx_env.nonce() < current_nonce { "nonce too low" } else { "nonce too high" };
            return Err(ErrorObject::owned(-32000, msg, None::<()>));
        }

        let base_fee = U256::from(476_190_476_190u64); 
        let (max_fee, priority_fee): (U256, U256) = if let TxEnvelope::Eip1559(ref inner) = tx_env {
            (U256::from(inner.tx().max_fee_per_gas), U256::from(inner.tx().max_priority_fee_per_gas))
        } else { (base_fee, base_fee) };
        let effective_gas_price = base_fee + priority_fee.min(max_fee.saturating_sub(base_fee));

        let (to, contract_address) = match tx_env.to() {
            TxKind::Call(addr) => (Some(addr), None),
            TxKind::Create => (None, Some(sender.create(tx_env.nonce())))
        };
        let recipient = contract_address.unwrap_or_else(|| to.unwrap_or(Address::ZERO));

        let mut s_bal = self.get_u256("bal", sender.as_slice());
        if s_bal < tx_env.value() { return Err(ErrorObject::owned(-32000, "Insufficient funds", None::<()>)); }
        
        s_bal -= tx_env.value();
        self.set_u256("bal", sender.as_slice(), s_bal);
        self.set_u256("bal", recipient.as_slice(), self.get_u256("bal", recipient.as_slice()) + tx_env.value());
        non_tree.insert(sender.as_slice(), &(current_nonce + 1).to_be_bytes()).unwrap();

        let h = self.db.get(b"bh").unwrap().map(|v| u64::from_be_bytes(v.as_ref().try_into().unwrap())).unwrap_or(1000) + 1;
        self.db.insert(b"bh", &h.to_be_bytes()).unwrap();

        let hash = keccak256(&bytes);
        let info = TransactionInfo {
            from: sender, to, contract_address, amount: tx_env.value(), block_number: h,
            hash, nonce: tx_env.nonce(), gas_limit: tx_env.gas_limit() as u64,
            effective_gas_price, max_fee, priority_fee, base_fee
        };

        self.db.open_tree("txs").unwrap().insert(hash.as_slice(), serde_json::to_vec(&info).unwrap()).unwrap();
        self.db.open_tree("block_txs").unwrap().insert(&h.to_be_bytes(), hash.as_slice()).unwrap();
        self.db.open_tree("base_fees").unwrap().insert(&h.to_be_bytes(), &base_fee.to_be_bytes::<32>()).unwrap();
        self.db.flush().unwrap();

        println!("💎 [PULSE] New TX in Block {}: {}... -> {}...", h, hex::encode(&sender.as_slice()[..4]), hex::encode(&recipient.as_slice()[..4]));
        Ok(format!("0x{}", hex::encode(hash)))
    }

    async fn get_transaction_receipt(&self, hash: B256) -> Result<Option<serde_json::Value>, ErrorObject<'static>> {
        if let Some(data) = self.db.open_tree("txs").unwrap().get(hash.as_slice()).unwrap() {
            let tx: TransactionInfo = serde_json::from_slice(&data).unwrap();
            Ok(Some(json!({
                "transactionHash": format!("0x{}", hex::encode(tx.hash)),
                "blockNumber": format!("0x{:x}", tx.block_number),
                "blockHash": format!("0x{}", hex::encode(keccak256(tx.block_number.to_be_bytes()))),
                "from": format!("0x{}", hex::encode(tx.from)),
                "to": if let Some(addr) = tx.to { json!(format!("0x{}", hex::encode(addr))) } else { json!(null) },
                "contractAddress": if let Some(addr) = tx.contract_address { json!(format!("0x{}", hex::encode(addr))) } else { json!(null) },
                "status": "0x1", "gasUsed": "0x5208", "cumulativeGasUsed": "0x5208", 
                "effectiveGasPrice": format!("0x{:x}", tx.effective_gas_price),
                "type": "0x2", "logs": [], "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
            })))
        } else { Ok(None) }
    }

    async fn get_block_by_number(&self, num: String, full: bool) -> Result<Option<serde_json::Value>, ErrorObject<'static>> {
        let h = if num == "latest" { self.db.get(b"bh").unwrap().map(|v| u64::from_be_bytes(v.as_ref().try_into().unwrap())).unwrap_or(1000) } 
                else { u64::from_str_radix(num.trim_start_matches("0x"), 16).unwrap_or(1000) };
        let b_hash = keccak256(h.to_be_bytes());
        let tx_hash = self.db.open_tree("block_txs").unwrap().get(&h.to_be_bytes()).unwrap();
        let base_fee = self.db.open_tree("base_fees").unwrap().get(&h.to_be_bytes()).unwrap().map(|v| U256::from_be_slice(&v)).unwrap_or(U256::from(476_190_476_190u64));
        
        let mut txs_json = json!([]);
        if let Some(h_bytes) = tx_hash {
            if full {
                let data = self.db.open_tree("txs").unwrap().get(&h_bytes).unwrap().unwrap();
                let tx: TransactionInfo = serde_json::from_slice(&data).unwrap();
                txs_json = json!([{
                    "hash": format!("0x{}", hex::encode(tx.hash)), "from": format!("0x{}", hex::encode(tx.from)),
                    "to": if let Some(a) = tx.to { json!(format!("0x{}", hex::encode(a))) } else { json!(null) },
                    "value": format!("0x{:x}", tx.amount), "nonce": format!("0x{:x}", tx.nonce),
                    "gas": format!("0x{:x}", tx.gas_limit), "maxFeePerGas": format!("0x{:x}", tx.max_fee),
                    "maxPriorityFeePerGas": format!("0x{:x}", tx.priority_fee), "type": "0x2",
                    "blockNumber": format!("0x{:x}", h), "blockHash": format!("0x{}", hex::encode(b_hash)), "transactionIndex": "0x0"
                }]);
            } else { txs_json = json!([format!("0x{}", hex::encode(h_bytes))]); }
        }

        Ok(Some(json!({
            "number": format!("0x{:x}", h), "hash": format!("0x{}", hex::encode(b_hash)), "parentHash": format!("0x{}", hex::encode(keccak256((h-1).to_be_bytes()))),
            "timestamp": "0x65e00000", "transactions": txs_json, "gasLimit": "0xffffff", "gasUsed": "0x5208", "baseFeePerGas": format!("0x{:x}", base_fee)
        })))
    }

    fn estimate_gas(&self) -> Result<String, ErrorObject<'static>> { Ok("0x5208".to_string()) }
    fn gas_price(&self) -> Result<String, ErrorObject<'static>> { Ok("0x6eda064000".to_string()) }
    fn max_priority_fee(&self) -> Result<String, ErrorObject<'static>> { Ok("0x0".to_string()) }
    async fn eth_call(&self, _tx: serde_json::Value, _b: String) -> Result<String, ErrorObject<'static>> { Ok("0x".to_string()) }
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let db = sled::open("uhu_db")?;
    let server = ServerBuilder::default().build(SocketAddr::from(([0, 0, 0, 0], 80))).await?;
    println!("💎 UHU PULSE ENGINE ONLINE!");
    server.start(UhuNode { db, state: Arc::new(RwLock::new(())) }.into_rpc()).stopped().await; Ok(())
}
