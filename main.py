import os

import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile

from models import DangerousTerrorists

app = FastAPI(title="ip-geolocation")

def is_connected()->bool:
    pass

def data_cleaning(terrorists):
    terrorists = terrorists.to_dict("records")
    print(terrorists)
    data = []

    for terrorist in terrorists:
        print(terrorist)
        data.append(DangerousTerrorists(name=terrorist["name"],
                                        location= terrorist["location"],
                                        danger_rate=terrorist["danger_rate"]))
    data.sort(key=lambda x: x.danger_rate, reverse=True)
    return data[:5]


@app.get("/health")
async def health_check():
    try:

        if is_connected():
            return {
                "status": "healthy",
                "redis": "connected",
            }
    except Exception as e:
        print(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Redis unavailable")


@app.post("/top-threats")
def top_threats(file: UploadFile):
    terrorists = pd.read_csv(file.file)
    top = data_cleaning(terrorists)

    return {
        "count": len(top),
        "top": top
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=os.getenv("DB_PORT", 8000),
        reload=True,
    )
