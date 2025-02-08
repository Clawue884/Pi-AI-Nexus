from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from config import web3, cipher
from ai_analysis import analyze_smart_contract

app = FastAPI()

class SmartContract(BaseModel):
    code: str
    owner: str

@app.post("/verify_contract")
async def verify_contract(contract: SmartContract):
    """ Verifikasi keamanan kontrak pintar menggunakan AI """
    risk_status = analyze_smart_contract(contract.code)
    return {"status": "success", "risk_status": risk_status}

@app.post("/deploy_contract")
async def deploy_contract(contract: SmartContract):
    """ Deploy smart contract di Pi Blockchain """
    if analyze_smart_contract(contract.code) == "Berisiko":
        raise HTTPException(status_code=400, detail="Kontrak memiliki celah keamanan!")

    compiled_contract = web3.eth.contract(abi=[], bytecode=contract.code)
    tx_hash = compiled_contract.constructor().transact({'from': contract.owner})
    return {"status": "success", "tx_hash": tx_hash.hex()}
