import json, requests
from pathlib import Path

BASE = Path(__file__).resolve().parent
cfg = json.loads((BASE / "config.json").read_text(encoding="utf-8"))

r = requests.post(cfg["discord_webhook"], json={"content": "🚨 Sneaker Bot Test Ping!"}, timeout=10)
print("Status:", r.status_code, "(204 means success)")
print("Response:", r.text)