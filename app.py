import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

# Configurar CORS para permitir peticiones desde cualquier origen (Frontend web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Almacenamiento en memoria para el último reporte del nodo
latest_metrics = {
    "hostname": "Sin datos",
    "ip": "--",
    "cpu_temp": "--°C",
    "ram_usage": "--%",
    "disk_usage": "--%",
    "docker_status": "Esperando conexión...",
}

# Credenciales de Telegram (puedes cambiarlas cuando tengas tu propio bot)
TELEGRAM_TOKEN = "8933668095:AAE9MQWYr5k9TLa_DUa_aFxYGI7rgRXghHI"
CHAT_ID = "8206383761"

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error enviando alerta de Telegram: {e}")

class MetricsModel(BaseModel):
    hostname: str
    ip: str
    cpu_temp: str
    ram_usage: str
    disk_usage: str
    docker_status: str

@app.post("/api/metrics")
def receive_metrics(metrics: MetricsModel):
    global latest_metrics
    latest_metrics = metrics.dict()
    
    # Análisis Inteligente de Alertas
    alerts = []
    
    # 1. Verificar temperatura CPU (ej. "58°C" -> 58.0)
    try:
        temp_val = float(metrics.cpu_temp.replace("°C", "").strip())
        if temp_val > 70.0:
            alerts.append(f"🔥 *Alerta de Temperatura*: El nodo *{metrics.hostname}* alcanzó los *{metrics.cpu_temp}*.")
    except ValueError:
        pass

    # 2. Verificar RAM (ej. "24.1%" -> 24.1)
    try:
        ram_val = float(metrics.ram_usage.replace("%", "").strip())
        if ram_val > 90.0:
            alerts.append(f"⚠️ *Alerta de Memoria RAM*: El nodo *{metrics.hostname}* está al *{metrics.ram_usage}*.")
    except ValueError:
        pass

    # Si se detecta alguna anomalía, disparar notificación a Telegram
    if alerts:
        alert_msg = "\n".join(alerts)
        send_telegram_alert(alert_msg)

    return {"status": "success", "message": "Métricas recibidas y analizadas"}

@app.get("/api/metrics")
def get_metrics():
    return latest_metrics

@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h3>NodePulse API está en línea. Usa /api/metrics</h3>"
