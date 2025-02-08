from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from config import users, transactions, encrypt_data, decrypt_data
from argon2 import PasswordHasher
import uuid

app = FastAPI()
ph = PasswordHasher()

class RegisterUser(BaseModel):
    username: str
    password: str

class LoginUser(BaseModel):
    username: str
    password: str

class Transaction(BaseModel):
    sender: str
    recipient: str
    amount: float

@app.post("/register")
async def register(user: RegisterUser):
    """ Registrasi pengguna dengan hash Argon2 """
    if users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username sudah ada")

    hashed_password = ph.hash(user.password)
    encrypted_password = encrypt_data(hashed_password)
    users.insert_one({"username": user.username, "password": encrypted_password})
    return {"status": "success", "message": "User berhasil terdaftar"}

@app.post("/login")
async def login(user: LoginUser):
    """ Login dengan verifikasi password Argon2 """
    user_data = users.find_one({"username": user.username})
    if not user_data:
        raise HTTPException(status_code=400, detail="User tidak ditemukan")

    try:
        decrypted_password = decrypt_data(user_data["password"])
        if ph.verify(decrypted_password, user.password):
            return {"status": "success", "message": "Login berhasil"}
        else:
            raise HTTPException(status_code=400, detail="Password salah")
    except:
        raise HTTPException(status_code=400, detail="Gagal memverifikasi password")

@app.post("/send_transaction")
async def send_transaction(tx: Transaction):
    """ Simpan transaksi terenkripsi di MongoDB """
    tx_id = str(uuid.uuid4())
    encrypted_sender = encrypt_data(tx.sender)
    encrypted_recipient = encrypt_data(tx.recipient)
    encrypted_amount = encrypt_data(str(tx.amount))

    transactions.insert_one({
        "tx_id": tx_id,
        "sender": encrypted_sender,
        "recipient": encrypted_recipient,
        "amount": encrypted_amount
    })

    return {"status": "success", "message": "Transaksi berhasil disimpan", "tx_id": tx_id}

@app.get("/transaction/{tx_id}")
async def get_transaction(tx_id: str):
    """ Ambil transaksi dan dekripsi datanya """
    tx = transactions.find_one({"tx_id": tx_id})
    if not tx:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")

    return {
        "tx_id": tx["tx_id"],
        "sender": decrypt_data(tx["sender"]),
        "recipient": decrypt_data(tx["recipient"]),
        "amount": decrypt_data(tx["amount"])
    }

# Jalankan server FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
