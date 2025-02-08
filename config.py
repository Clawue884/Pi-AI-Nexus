import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64encode, b64decode
from pymongo import MongoClient

# Konfigurasi MongoDB
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["pi_secure_db"]
users = db["users"]
transactions = db["transactions"]

# Kunci AES (32-byte untuk AES-256)
AES_KEY = os.getenv("AES_KEY", "16bytessecretskey!!32byteskey123456")

def encrypt_data(data: str) -> str:
    """ Enkripsi data dengan AES-256 """
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(AES_KEY.encode()), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padded_data = data.ljust(32)  # Padding ke 32 byte
    encrypted_data = encryptor.update(padded_data.encode()) + encryptor.finalize()
    return b64encode(iv + encrypted_data).decode()

def decrypt_data(data: str) -> str:
    """ Dekripsi data AES-256 """
    raw_data = b64decode(data)
    iv, encrypted_data = raw_data[:16], raw_data[16:]
    cipher = Cipher(algorithms.AES(AES_KEY.encode()), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted_data).decode().strip()
