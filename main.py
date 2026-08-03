import os
import json
import base64
import hashlib
import firebase_admin
from firebase_admin import credentials, db
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

firebase_json = os.environ.get('FIREBASE_CONFIG')
database_url = os.environ.get('DATABASE_URL')
aes_key_str = os.environ.get('AES_KEY')

if not firebase_admin._apps:
    cred_dict = json.loads(firebase_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': database_url
    })

def encrypt_data(plain_text, secret_key):
    key = hashlib.sha256(secret_key.encode('utf-8')).digest()
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(plain_text.encode('utf-8'), AES.block_size)
    encrypted = cipher.encrypt(padded_data)
    return base64.b64encode(iv + encrypted).decode('utf-8')

def fetch_and_save():
    root_ref = db.reference('/')
    all_data = root_ref.get()
    
    excluded_keys = {'Highlights', 'delete_channels', 'delete_events'}
    
    filtered_data = {}
    if all_data and isinstance(all_data, dict):
        filtered_data = {
            key: value for key, value in all_data.items() 
            if key not in excluded_keys
        }
    
    json_str = json.dumps(filtered_data, ensure_ascii=False)
    encrypted_str = encrypt_data(json_str, aes_key_str)
    
    payload = {
        "data": encrypted_str
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=4, ensure_ascii=False)
        
    print("Success: data.json created")

if __name__ == "__main__":
    fetch_and_save()
