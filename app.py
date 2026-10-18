import os
import requests
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

latest_metrics = {
    "hostname": "Sin datos",
    "ip": "--",
    "cpu_temp": "--°C",
    "ram_usage": "--%",
    "disk_usage": "--%",
    "docker_status": "Esperando conexión...",
}

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")
SERVER_API_KEY = os.getenv("SERVER_API_KEY", "nodepulse_secreto_2026")

def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error enviando alerta: {e}")

class MetricsModel(BaseModel):
    hostname: str
    ip: str
    cpu_temp: str
    ram_usage: str
    disk_usage: str
    docker_status: str

@app.post("/api/metrics")
def receive_metrics(metrics: MetricsModel, x_api_key: str = Header(None)):
    if x_api_key != SERVER_API_KEY:
        raise HTTPException(status_code=403, detail="No autorizado: API Key incorrecta")

    global latest_metrics
    latest_metrics = metrics.dict()
    
    alerts = []
    try:
        temp_val = float(metrics.cpu_temp.replace("°C", "").strip())
        if temp_val > 70.0:
            alerts.append(f"🔥 *Alerta de Temperatura*: El nodo *{metrics.hostname}* alcanzó los *{metrics.cpu_temp}*.")
    except ValueError:
        pass

    try:
        ram_val = float(metrics.ram_usage.replace("%", "").strip())
        if ram_val > 90.0:
            alerts.append(f"⚠️ *Alerta de Memoria RAM*: El nodo *{metrics.hostname}* está al *{metrics.ram_usage}*.")
    except ValueError:
        pass

    if alerts:
        alert_msg = "\n".join(alerts)
        send_telegram_alert(alert_msg)

    return {"status": "success", "message": "Métricas recibidas de forma segura"}

@app.get("/api/metrics")
def get_metrics():
    return latest_metrics

@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h3>NodePulse API Segura</h3>"
