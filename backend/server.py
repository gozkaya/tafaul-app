from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
import random
import httpx


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Language mappings
LANGUAGE_MAPPINGS = {
    'ar': {'code': 'ar.alafasy', 'name': 'العربية (Arabic)', 'flag': '🇸🇦'},
    'zh': {'code': 'zh.jian', 'name': '中文 (Chinese)', 'flag': '🇨🇳'},
    'nl': {'code': 'nl.keyzer', 'name': 'Nederlands (Dutch)', 'flag': '🇳🇱'},
    'en': {'code': 'en.sahih', 'name': 'English', 'flag': '🇬🇧'},
    'fi': {'code': 'fi.finnish', 'name': 'Suomi (Finnish)', 'flag': '🇫🇮'},
    'fr': {'code': 'fr.hamidullah', 'name': 'Français (French)', 'flag': '🇫🇷'},
    'de': {'code': 'de.bubenheim', 'name': 'Deutsch (German)', 'flag': '🇩🇪'},
    'no': {'code': 'no.berg', 'name': 'Norsk (Norwegian)', 'flag': '🇳🇴'},
    'ru': {'code': 'ru.kuliev', 'name': 'Русский (Russian)', 'flag': '🇷🇺'},
    'es': {'code': 'es.cortes', 'name': 'Español (Spanish)', 'flag': '🇪🇸'},
    'sv': {'code': 'sv.bernstrom', 'name': 'Svenska (Swedish)', 'flag': '🇸🇪'},
    'tr': {'code': 'tr.ates', 'name': 'Türkçe (Turkish)', 'flag': '🇹🇷'},
    'uk': {'code': 'uk.korkmasov', 'name': 'Українська (Ukrainian)', 'flag': '🇺🇦'},
    'ur': {'code': 'ur.jalandhry', 'name': 'اردو (Urdu)', 'flag': '🇵🇰'},
}

# Define Models
class VerseResponse(BaseModel):
    surah_number: int
    surah_name: str
    surah_name_arabic: str
    verse_number: int
    arabic_text: str
    translation: str
    language: str
    reference: str

class LanguageInfo(BaseModel):
    code: str
    name: str
    flag: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Quran Verse Generator API"}

@api_router.get("/languages")
async def get_languages():
    """Get list of supported languages"""
    return [
        {"code": code, "name": info['name'], "flag": info['flag']}
        for code, info in LANGUAGE_MAPPINGS.items()
    ]

@api_router.get("/random-verse")
async def get_random_verse(language: str = "en"):
    """Get a random verse from the Quran with translation"""
    
    if language not in LANGUAGE_MAPPINGS:
        raise HTTPException(status_code=400, detail=f"Language '{language}' not supported")
    
    # Generate random verse (total verses in Quran: 6236)
    random_verse_number = random.randint(1, 6236)
    
    # Get translation code
    translation_code = LANGUAGE_MAPPINGS[language]['code']
    
    try:
        async with httpx.AsyncClient() as client:
            # Fetch the verse with Arabic text and translation
            url = f"https://api.alquran.cloud/v1/ayah/{random_verse_number}/editions/quran-uthmani,{translation_code}"
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] != 200:
                raise HTTPException(status_code=500, detail="Failed to fetch verse from Quran API")
            
            # Extract Arabic and translation
            arabic_data = data['data'][0]
            translation_data = data['data'][1]
            
            return VerseResponse(
                surah_number=arabic_data['surah']['number'],
                surah_name=arabic_data['surah']['englishName'],
                surah_name_arabic=arabic_data['surah']['name'],
                verse_number=arabic_data['numberInSurah'],
                arabic_text=arabic_data['text'],
                translation=translation_data['text'],
                language=LANGUAGE_MAPPINGS[language]['name'],
                reference=f"Surah {arabic_data['surah']['englishName']} ({arabic_data['surah']['number']}:{arabic_data['numberInSurah']})"
            )
    
    except httpx.HTTPError as e:
        logging.error(f"HTTP error fetching verse: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch verse from external API")
    except Exception as e:
        logging.error(f"Error fetching verse: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
