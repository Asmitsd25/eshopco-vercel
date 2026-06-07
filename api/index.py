from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

from pathlib import Path

data_file = Path(__file__).parent.parent / "q-vercel-latency.json"

with open(data_file, "r") as f:
    DATA = json.load(f)

class RequestBody(BaseModel):
    regions: List[str]
    threshold_ms: float
    
@app.get("/")
def health():
    return {"status": "ok"}
    
@app.post("/")
def calculate_metrics(req: RequestBody):

    result = {}

    for region in req.regions:

        rows = [
            r for r in DATA
            if r["region"] == region
        ]

        latencies = [
            r["latency_ms"]
            for r in rows
        ]

        uptimes = [
            r["uptime_pct"]
            for r in rows
        ]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 3),
            "breaches": sum(
                1
                for x in latencies
                if x > req.threshold_ms
            )
        }

    return result
