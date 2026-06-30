"""
VPS'te çalışacak basit API.
- Yerel bilgisayar buraya POST /api/sayi ile veri gönderir.
- Web sayfası GET /api/sayi ile son veriyi okur.
- Bilgisayar bir süredir veri göndermemişse "offline" durumu döner.

Kurulum:
    pip install fastapi uvicorn

Render.com'da start command:
    uvicorn server:app --host 0.0.0.0 --port $PORT
"""

import time
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

API_KEY = "gizli-anahtar-buraya"   # local_counter.py'deki ile AYNI olmalı
OFFLINE_ESIK_SANIYE = 30           # bu süre veri gelmezse "offline" say

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # istersen sadece kendi domainine kısıtla
    allow_methods=["*"],
    allow_headers=["*"],
)

durum = {
    "kisi_sayisi": 0,
    "son_guncelleme": 0,
}


class VeriGiris(BaseModel):
    kisi_sayisi: int
    zaman: float


@app.get("/")
def ana_sayfa():
    return FileResponse("index.html")


@app.post("/api/sayi")
def veri_al(veri: VeriGiris, authorization: str = Header(default="")):
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Yetkisiz")

    durum["kisi_sayisi"] = veri.kisi_sayisi
    durum["son_guncelleme"] = time.time()
    return {"durum": "ok"}


@app.get("/api/sayi")
def veri_oku():
    simdi = time.time()
    cevrimici = (simdi - durum["son_guncelleme"]) < OFFLINE_ESIK_SANIYE if durum["son_guncelleme"] else False

    return {
        "kisi_sayisi": durum["kisi_sayisi"] if cevrimici else None,
        "cevrimici": cevrimici,
        "son_guncelleme": durum["son_guncelleme"],
    }
