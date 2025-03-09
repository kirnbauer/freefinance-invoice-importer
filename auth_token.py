# auth_token.py

import json
import os
import time
import requests
from config import USERNAME, PAIRING_CODE, CLIENT_ID, API_URL

TOKEN_FILE = "token.json"

def save_token(data: dict):
    data["expires_at"] = time.time() + data.get("expires_in", 3600)
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f)

def load_token() -> dict:
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return {}

def is_token_valid(token_data: dict) -> bool:
    return token_data.get("access_token") and time.time() < token_data.get("expires_at", 0)

def authenticate_pairing() -> str:
    """Initiale Authentifizierung per Pairing-Code (grant_type=password)."""
    url = f"{API_URL}/oauth2/token"
    payload = {
        'grant_type': 'password',
        'username': USERNAME,
        'password': PAIRING_CODE,
        'client_id': CLIENT_ID
    }
    resp = requests.post(url, data=payload)
    resp.raise_for_status()
    token_data = resp.json()
    save_token(token_data)
    return token_data["access_token"]

def refresh_access_token(token_data: dict) -> str:
    """Erneuert den Access Token per Refresh-Token (grant_type=refresh_token)."""
    url = f"{API_URL}/oauth2/token"
    payload = {
        'grant_type':    'refresh_token',
        'refresh_token': token_data.get("refresh_token"),
        'client_id':     CLIENT_ID
    }
    resp = requests.post(url, data=payload)
    resp.raise_for_status()
    new_data = resp.json()
    save_token(new_data)
    return new_data["access_token"]

def get_access_token() -> str:
    """
    Gibt einen gültigen Access Token zurück.
    1) Wenn ein gültiges token.json existiert, verwende es.
    2) Falls abgelaufen, versuche Refresh-Flow.
    3) Falls kein Refresh-Token oder Refresh schlägt fehl, starte Pairing-Flow.
    """
    token_data = load_token()

    if is_token_valid(token_data):
        return token_data["access_token"]

    # Token abgelaufen: versuche Refresh
    refresh_token = token_data.get("refresh_token")
    if refresh_token:
        try:
            print("🔄 Versuche, Access Token per Refresh-Token zu erneuern...")
            return refresh_access_token(token_data)
        except requests.exceptions.HTTPError as e:
            print(f"❌ Refresh fehlgeschlagen ({e}); neuer Pairing-Code wird benötigt.")

    # Fallback: neuer Pairing-Code
    print("🔑 Hole neuen Access Token via Pairing-Code …")
    return authenticate_pairing()
