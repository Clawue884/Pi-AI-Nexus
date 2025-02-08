from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from web3 import Web3
from pymongo import MongoClient
import os

# Koneksi Web3 ke Pi Blockchain
PI_RPC_URL = "https://api.pi-network.io"
web3 = Web3(Web3.HTTPProvider(PI_RPC_URL))

# Koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["pi_web3"]
transactions = db["transactions"]

# Kontrak pintar (contoh)
CONTRACT_ADDRESS = "0x1234567890abcdef1234567890abcdef12345678"
CONTRACT_ABI = []  # Tambahkan ABI kontrak di sini
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# Model API
class TransactionRequest(BaseModel):
    sender: str
    recipient: str
    amount: float

# API Kirim Transaksi Pi
app = FastAPI()

@app.post("/send_transaction")
async def send_transaction(tx: TransactionRequest):
    try:
        sender_balance = web3.eth.get_balance(tx.sender)
        if sender_balance < web3.to_wei(tx.amount, "ether"):
            raise HTTPException(status_code=400, detail="Saldo tidak cukup")

        nonce = web3.eth.get_transaction_count(tx.sender)
        transaction = {
            "to": tx.recipient,
            "value": web3.to_wei(tx.amount, "ether"),
            "gas": 21000,
            "gasPrice": web3.to_wei("5", "gwei"),
            "nonce": nonce,
            "chainId": 314  # Chain ID untuk Pi Network
        }

        signed_txn = web3.eth.account.sign_transaction(transaction, os.getenv("PRIVATE_KEY"))
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        transactions.insert_one({"sender": tx.sender, "recipient": tx.recipient, "amount": tx.amount, "tx_hash": tx_hash.hex()})
        return {"status": "success", "tx_hash": tx_hash.hex()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API Eksekusi Kontrak Pintar
@app.post("/execute_contract")
async def execute_contract(data: dict):
    try:
        sender = data["sender"]
        function_name = data["function"]
        args = data.get("args", [])

        contract_function = contract.functions[function_name](*args)
        nonce = web3.eth.get_transaction_count(sender)

        transaction = contract_function.build_transaction({
            "from": sender,
            "gas": 1000000,
            "gasPrice": web3.to_wei("5", "gwei"),
            "nonce": nonce,
        })

        signed_txn = web3.eth.account.sign_transaction(transaction, os.getenv("PRIVATE_KEY"))
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        return {"status": "success", "tx_hash": tx_hash.hex()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Jalankan API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
