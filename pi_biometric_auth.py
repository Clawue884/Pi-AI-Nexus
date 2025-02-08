from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import secrets
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from pymongo import MongoClient
from web3 import Web3

# Inisialisasi FastAPI
app = FastAPI()

# Koneksi ke MongoDB (Database autentikasi biometrik)
client = MongoClient("mongodb://localhost:27017/")
db = client["pi_biometric"]
users = db["users"]

# Kunci enkripsi AES
AES_KEY = secrets.token_bytes(32)

# Inisialisasi Web3 untuk transaksi Pi Blockchain
web3 = Web3(Web3.HTTPProvider("https://api.pi-network.io"))

# Kontrak pintar (contoh address)
CONTRACT_ADDRESS = "0x1234567890abcdef1234567890abcdef12345678"
CONTRACT_ABI = []  # Tambahkan ABI Kontrak di sini

# Inisialisasi Kontrak Pi
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# Model Input
class BiometricRequest(BaseModel):
    user_id: str
    fingerprint_data: str

class TransactionRequest(BaseModel):
    sender: str
    recipient: str
    amount: float

# Fungsi Enkripsi AES
def encrypt_data(data):
    iv = secrets.token_bytes(16)
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv))
    encryptor = cipher.encryptor()
    padded_data = data + " " * (16 - len(data) % 16)  # Padding
    encrypted = encryptor.update(padded_data.encode()) + encryptor.finalize()
    return base64.b64encode(iv + encrypted).decode()

# Fungsi Dekripsi AES
def decrypt_data(encrypted_data):
    decoded = base64.b64decode(encrypted_data)
    iv, encrypted = decoded[:16], decoded[16:]
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv))
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted) + decryptor.finalize()

# API untuk Registrasi Sidik Jari
@app.post("/register_biometric")
async def register_biometric(data: BiometricRequest):
    encrypted_fingerprint = encrypt_data(data.fingerprint_data)
    users.insert_one({"user_id": data.user_id, "fingerprint": encrypted_fingerprint})
    return {"status": "registered"}

# API untuk Autentikasi Sidik Jari
@app.post("/authenticate_biometric")
async def authenticate_biometric(data: BiometricRequest):
    user = users.find_one({"user_id": data.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    decrypted_fingerprint = decrypt_data(user["fingerprint"]).strip()
    if decrypted_fingerprint == data.fingerprint_data:
        return {"status": "authenticated"}
    else:
        raise HTTPException(status_code=401, detail="Biometric mismatch")

# API untuk Kirim Transaksi Pi setelah autentikasi biometrik
@app.post("/send_transaction")
async def send_transaction(tx: TransactionRequest):
    tx_hash = contract.functions.transfer(tx.recipient, web3.to_wei(tx.amount, "ether")).transact({"from": tx.sender})
    return {"status": "success", "tx_hash": tx_hash.hex()}

# Jalankan server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
