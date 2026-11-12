import os 
from contextlib import asynccontextmanager
from datetime import datetime

import httpx
from fastapi import FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db import Base, Rate, engine

CBR_URL = os.getenv("CBR_URL", "https://www.cbr-xml-daily.ru/daily_json.js")
CURRENCIES = ["USD", "EUR", "CNY"]

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="CBR Rates", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.4.0"}


@app.get("/rates")
def rates():
    try:
        resp = httpx.get(CBR_URL, timeout=10)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Источник курсов недоступен: {e}")

    data = resp.json()
    rate_date = datetime.fromisoformat(data["Date"])
    values = {code: data["Valute"][code]["Value"] for code in CURRENCIES}

    with Session(engine) as session:
        stmt = insert(Rate).values(
            [
                {"rate_date": rate_date, "currency": code, "value": value}
                for code, value in values.items()
            ]
        ).on_conflict_do_nothing(index_elements=["rate_date", "currency"])
        session.execute(stmt)
        session.commit()

    return {"date": data["Date"], "rates": values}

@app.get("/rates/history")
def rates_history(limit: int = 30):
    with Session(engine) as session:
        rows = session.scalars(
            select(Rate).order_by(Rate.rate_date.desc(), Rate.currency).limit(limit)
        ).all()

    return [
        {"date": r.rate_date.isoformat(), "currency": r.currency, "value": float(r.value)}
        for r in rows
    ]