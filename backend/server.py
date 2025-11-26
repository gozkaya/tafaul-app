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

async def fetch_verse_with_fallback(verse_number: int, translation_code: str):
    """
    Fetch verse with multiple API fallbacks for redundancy
    """
    # Primary API: Al-Quran Cloud
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://api.alquran.cloud/v1/ayah/{verse_number}/editions/quran-uthmani,{translation_code}"
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] == 200:
                return {'source': 'alquran.cloud', 'data': data['data']}
    except Exception as e:
        logging.warning(f"Primary API (alquran.cloud) failed: {e}")
    
    # Fallback API 1: Quran.com API
    try:
        async with httpx.AsyncClient() as client:
            # Get verse info
            url = f"https://api.quran.com/api/v4/verses/by_key/{verse_number}?words=false&translations={translation_code}"
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            # Transform to our format
            verse_data = data.get('verse', {})
            # Note: This is a simplified fallback - in production you'd handle the full transformation
            return {'source': 'quran.com', 'data': data}
    except Exception as e:
        logging.warning(f"Fallback API 1 (quran.com) failed: {e}")
    
    # Fallback API 2: QuranEnc.com (if previous fail)
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://quranenc.com/api/v1/translation/aya/english_saheeh/{verse_number}"
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return {'source': 'quranenc.com', 'data': data}
    except Exception as e:
        logging.warning(f"Fallback API 2 (quranenc.com) failed: {e}")
    
    # All APIs failed
    raise HTTPException(status_code=503, detail="All Quran API services are currently unavailable. Please try again later.")


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
        result = await fetch_verse_with_fallback(random_verse_number, translation_code)
        
        # Extract Arabic and translation (from primary API format)
        if result['source'] == 'alquran.cloud':
            arabic_data = result['data'][0]
            translation_data = result['data'][1]
            
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
        else:
            # Handle other API formats if needed
            raise HTTPException(status_code=500, detail="Unsupported API response format")
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching verse: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@api_router.get("/verse/{surah_number}/{verse_number}")
async def get_specific_verse(surah_number: int, verse_number: int, language: str = "en"):
    """Get a specific verse by surah and verse number with translation"""
    
    if language not in LANGUAGE_MAPPINGS:
        raise HTTPException(status_code=400, detail=f"Language '{language}' not supported")
    
    # Calculate absolute verse number
    # This is a simplified approach - in production you'd have a proper mapping
    try:
        async with httpx.AsyncClient() as client:
            # Get surah info to calculate absolute verse number
            surah_url = f"https://api.alquran.cloud/v1/surah/{surah_number}"
            surah_response = await client.get(surah_url, timeout=10.0)
            surah_response.raise_for_status()
            surah_data = surah_response.json()
            
            if surah_data['code'] != 200:
                raise HTTPException(status_code=404, detail="Surah not found")
            
            # Get the specific ayah
            ayahs = surah_data['data']['ayahs']
            target_ayah = None
            for ayah in ayahs:
                if ayah['numberInSurah'] == verse_number:
                    target_ayah = ayah
                    break
            
            if not target_ayah:
                raise HTTPException(status_code=404, detail="Verse not found in surah")
            
            absolute_verse_number = target_ayah['number']
            
            # Get translation code
            translation_code = LANGUAGE_MAPPINGS[language]['code']
            
            # Fetch the verse with fallback
            result = await fetch_verse_with_fallback(absolute_verse_number, translation_code)
            
            # Extract Arabic and translation
            if result['source'] == 'alquran.cloud':
                arabic_data = result['data'][0]
                translation_data = result['data'][1]
                
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
            else:
                raise HTTPException(status_code=500, detail="Unsupported API response format")
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching specific verse: {e}")
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
async def shutdown_event():
    logging.info("Application shutting down")
