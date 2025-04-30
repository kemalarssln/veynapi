import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
from dotenv import load_dotenv
import openai

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

@app.post("/soru-uret")
async def soru_uret(istek: SoruIstek):
    logger.info(f"Soru üretim isteği: {istek}")
    sinif_no = ''.join(filter(str.isdigit, istek.sinif))
    dersler_konular = sinif_ders_konular.get(sinif_no, {})
    dersler_str = '; '.join([f"{ders}: {', '.join(konular)}" for ders, konular in dersler_konular.items()])
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
