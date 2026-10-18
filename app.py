from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MetricData(BaseModel):
    hostname: str
    ip: str
    cpu_temp: str
    ram_usage: str
    disk_usage: str
    docker_status: str

latest_metrics = {
    "hostname": "Sin datos",
    "ip": "0.0.0.0",
    "cpu_temp": "0°C",
    "ram_usage": "0%",
    "disk_usage": "0%",
    "docker_status": "Desconocido"
}

@app.get("/api/metrics")
def get_metrics():
    return latest_metrics

@app.post("/api/metrics")
def receive_metrics(data: MetricData):
    global latest_metrics
    latest_metrics = data.dict()
    return {"status": "ok"}