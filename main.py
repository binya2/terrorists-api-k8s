import io
import logging
import os

import pandas as pd
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pymongo.errors import ConnectionFailure

from db import insert_threats, mongodb_check_connection
from models import Terrorist, TopThreatsResponse

app = FastAPI(title="Terrorists API")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def clean_data_to_saving_and_returning(file: UploadFile) -> list:
    """Sorting and returning the most dangerous terrorists"""
    content = await file.read()
    csv_string = content.decode('utf-8')
    df = pd.read_csv(io.StringIO(csv_string))
    required_columns = {'name', 'location', 'danger_rate'}
    if not required_columns.issubset(df.columns):
        raise HTTPException(status_code=422, detail="CSV missing required columns")
    df_sorted = df.sort_values(by='danger_rate', ascending=False)
    top_5_df = df_sorted.head(5)
    threats_list = []
    for _, row in top_5_df.iterrows():
        try:
            threat = Terrorist(
                name=str(row['name']),
                location=str(row['location']),
                danger_rate=row['danger_rate']
            )
            threats_list.append(threat.model_dump())
        except ValueError as e:
            logger.warning(f"Skipping invalid row: {e}")
            continue
    return threats_list


@app.get("/health")
async def health_check() -> dict | None:
    """Checking connection to mongodb"""
    try:
        if mongodb_check_connection():
            return {
                "status": "healthy",
                "MongoBD": "connected",
            }
    except Exception as e:
        print(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="MongoBD unavailable")


@app.post("/top-threats", response_model=TopThreatsResponse)
async def upload_threats(file: UploadFile = File(...)) -> JSONResponse | None:
    """Receiving CSV files with information about terrorists, saving and returning the most dangerous terrorists"""
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid CSV file")
    try:
        threats_list = await clean_data_to_saving_and_returning(file)
        insert_threats(threats_list)
        count = len(threats_list)
        response_data = {
            "top": threats_list,
            "count": count
        }
        return JSONResponse(content=response_data, status_code=200)
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Invalid CSV file")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Invalid CSV file")
    except ConnectionFailure:
        raise HTTPException(status_code=503, detail="MongoBD unavailable")
    except Exception as e:
        logger.error(f"Internal error: {str(e)}")
        if "validation error" in str(e).lower():
            raise HTTPException(status_code=422, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=os.getenv("DB_PORT", 8000),
        reload=True,
    )
