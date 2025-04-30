import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
from dotenv import load_dotenv
import openai
from typing import Dict, List

load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")  # eski satır

# Yeni OpenAI client'ı oluştur
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# CORS ayarı: Her yerden erişim (gerekirse domain kısıtlaması eklenebilir)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SoruIstek(BaseModel):
    ulke: str = "Türkiye"
    sinif: str = "3. sınıf"
    ders: str = ""
    konu: str = ""
    tip: str = "çoktan seçmeli"

# Sınıfa göre ders ve konu listesi kaldırıldı

# Türkiye için örnek sınıf-ders-konular veri yapısı
TURKIYE_SINIF_DERS_KONU: Dict[str, Dict[str, List[str]]] = {
    "1. sınıf": {
        "Matematik": ["Toplama İşlemi", "Çıkarma İşlemi", "Sayılar"],
        "Türkçe": ["Okuma Anlama", "Harfler", "Kısa Hikaye"]
    },
    "2. sınıf": {
        "Matematik": ["Çarpma İşlemi", "Bölme İşlemi", "Geometri"],
        "Türkçe": ["Dil Bilgisi", "Paragraf", "Yazım Kuralları"]
    },
    "6. sınıf": {
        "Matematik": ["Kesirler", "Cebirsel İfadeler", "Geometri"],
        "Fen Bilimleri": ["Vücudumuzdaki Sistemler", "Kuvvet ve Hareket"]
    },
    "7. sınıf": {
        "Matematik": ["Oran Orantı", "Denklemler"],
        "Fen Bilimleri": ["Hücre ve Genetik Kod", "Işık ve Ses"]
    },
    # ... diğer sınıflar eklenebilir ...
}

@app.post("/soru-uret")
async def soru_uret(istek: SoruIstek):
    logger.info(f"Soru üretim isteği: {istek}")
    prompt = (
        f"Sen bir eğitim uzmanısın. {istek.ulke} ülkesinde yaşayan, {istek.sinif} öğrencisi bir çocuk için, "
        f"yalnızca {istek.sinif} seviyesine uygun derslerden ve o derslerin gerçek, güncel müfredat konularından rastgele birini seç. "
        f"Her seferinde farklı, yaratıcı, özgün ve daha önce sormadığın bir {istek.tip} soru üret. "
        f"Sorular çocuğun yaşına uygun, anlaşılır, kısa ama net ve çeşitli olmalı. "
        f"Soru 4 şık ve doğru cevabı ile birlikte, konu başlığını ve ders adını da içersin. "
        f"Cevap formatı: {{\"soru\": \"...\", \"secenekler\": [\"A\", \"B\", \"C\", \"D\"], \"dogru_cevap\": \"A\", \"konu\": \"...\", \"ders\": \"...\", \"tip\": \"...\", \"zorluk\": \"...\"}}. "
        "Soruda asla resim, görsel, tablo veya herhangi bir medya bulunmasın, sadece metin tabanlı soru üret. "
        "Gereksiz açıklama, boşluk veya tekrar ekleme. Sadece JSON çıktısı ver."
    )
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=1.0,
        )
        logger.info("OpenAI'dan yanıt alındı.")
        cevap = response.choices[0].message.content
        logger.debug(f"OpenAI cevabı: {cevap}")
        return {"soru_json": cevap}
    except Exception as e:
        logger.error(f"Hata oluştu: {e}")
        raise HTTPException(status_code=500, detail="Soru üretilemedi. Lütfen tekrar deneyin.")

@app.get("/kullanici-ders-konulari")
async def kullanici_ders_konulari(
    ulke: str = Query(...),
    sinif: str = Query(...)
):
    if ulke != "Türkiye":
        return {"dersler": {}, "uyari": "Şu an sadece Türkiye destekleniyor."}
    dersler = TURKIYE_SINIF_DERS_KONU.get(sinif, {})
    return {"dersler": dersler} 
