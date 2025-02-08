from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from config import web3, encrypt_data
from consensus import Consensus

app = FastAPI()
consensus = Consensus()

class Transaction(BaseModel):
    sender: str
    receiver: str
    amount: float
    signature: str

@app.post("/validate_transaction")
async def validate_transaction(tx: Transaction):
    """ Validasi transaksi dengan AI-PoS """
    if tx.sender == tx.receiver:
        raise HTTPException(status_code=400, detail="Transaksi tidak valid: pengirim & penerima sama!")

    encrypted_data = encrypt_data(f"{tx.sender}-{tx.receiver}-{tx.amount}")
    return {"status": "success", "encrypted_data": encrypted_data.hex()}

@app.post("/stake")
async def stake_pi(address: str, amount: float):
    """ Stake Pi Coin untuk menjadi validator """
    consensus.stake(address, amount)
    return {"status": "success", "new_stake": consensus.stakers[address]}

@app.get("/validators")
async def get_validators():
    """ Mendapatkan daftar validator aktif """
    return {"status": "success", "validators": consensus.select_validators()}
