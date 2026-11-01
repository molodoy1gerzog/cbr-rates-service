import os 

import httpx
from fastapi import FastAPI, HTTPException

CBR_URL = os.getenv("CBR_URL", "https://www.cbr-xml-daily.ru/daily_json.js")
CURRENCIES = ["USD", "EUR", "CNY"]

app = FastAPI(title="CBR Rates")


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.2.0"}


@app.get("/rates")
def rates():
    try:
        resp = httpx.get(CBR_URL, timeout=10)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Источник курсов недоступен: {e}")

    data = resp.json()
    return {
        "date": data["Date"],
        "rates": {code: data["Valute"][code]["Value"] for code in CURRENCIES},
    }