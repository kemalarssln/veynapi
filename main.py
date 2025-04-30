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
    ulke: str
    sinif: str
    ders: str
    konu: str
    tip: str = "çoktan seçmeli"

@app.post("/soru-uret")
async def soru_uret(istek: SoruIstek):
    logger.info(f"Soru üretim isteği: {istek}")
    prompt = (
        f"Sen bir eğitim uzmanısın. {istek.ulke} ülkesinde yaşayan, yaşı {istek.sinif.replace('sınıf', '').strip()} olan bir çocuk için, "
        f"her seferinde rastgele bir ders (ör. matematik, fen, sosyal, Türkçe, İngilizce, hayat bilgisi, vs.) ve o derse ait rastgele bir konu seç. "
        f"Seçtiğin ders ve konuya uygun, yaşına göre anlaşılır, kısa ama net, özgün ve daha önce sormadığın bir {istek.tip} soru üret. "
        f"Soru 4 şık ve doğru cevabı ile birlikte, konu başlığını da içersin. Cevap formatı: {{\"soru\": \"...\", \"secenekler\": [\"A\", \"B\", \"C\", \"D\"], \"dogru_cevap\": \"A\", \"konu\": \"...\", \"ders\": \"...\"}}. "
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
