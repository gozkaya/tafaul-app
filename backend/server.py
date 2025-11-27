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

# Language mappings (sorted alphabetically)
LANGUAGE_MAPPINGS = {
    'ar': {'code': 'ar.alafasy', 'name': 'العربية (Arabic)', 'flag': '🇸🇦'},
    'bn': {'code': 'bn.bengali', 'name': 'বাংলা (Bengali)', 'flag': '🇧🇩'},
    'zh': {'code': 'zh.jian', 'name': '中文 (Chinese)', 'flag': '🇨🇳'},
    'en': {'code': 'en.sahih', 'name': 'English', 'flag': '🇬🇧'},
    'fr': {'code': 'fr.hamidullah', 'name': 'Français (French)', 'flag': '🇫🇷'},
    'de': {'code': 'de.bubenheim', 'name': 'Deutsch (German)', 'flag': '🇩🇪'},
    'hi': {'code': 'hi.hindi', 'name': 'हिन्दी (Hindi)', 'flag': '🇮🇳'},
    'id': {'code': 'id.indonesian', 'name': 'Bahasa Indonesia (Indonesian)', 'flag': '🇮🇩'},
    'ja': {'code': 'ja.japanese', 'name': '日本語 (Japanese)', 'flag': '🇯🇵'},
    'ms': {'code': 'ms.basmeih', 'name': 'Bahasa Melayu (Malay)', 'flag': '🇲🇾'},
    'pt': {'code': 'pt.elhayek', 'name': 'Português (Portuguese)', 'flag': '🇧🇷'},
    'ru': {'code': 'ru.kuliev', 'name': 'Русский (Russian)', 'flag': '🇷🇺'},
    'es': {'code': 'es.cortes', 'name': 'Español (Spanish)', 'flag': '🇪🇸'},
    'sw': {'code': 'sw.barwani', 'name': 'Kiswahili (Swahili)', 'flag': '🇰🇪'},
    'ta': {'code': 'ta.tamil', 'name': 'தமிழ் (Tamil)', 'flag': '🇮🇳'},
    'tr': {'code': 'tr.ates', 'name': 'Türkçe (Turkish)', 'flag': '🇹🇷'},
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

async def fetch_verse_with_fallback(verse_number: int, translation_code: str, max_retries: int = 3):
    """
    Fetch verse with multiple API fallbacks and retry logic for maximum redundancy
    """
    import asyncio
    
    # Primary API: Al-Quran Cloud with retry logic
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                url = f"https://api.alquran.cloud/v1/ayah/{verse_number}/editions/quran-uthmani,{translation_code}"
                response = await client.get(url, timeout=15.0)  # Increased timeout
                response.raise_for_status()
                data = response.json()
                
                if data['code'] == 200:
                    logging.info(f"Successfully fetched verse {verse_number} from primary API (attempt {attempt + 1})")
                    return {'source': 'alquran.cloud', 'data': data['data']}
        except httpx.TimeoutException as e:
            logging.warning(f"Primary API timeout (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                continue
        except httpx.HTTPStatusError as e:
            logging.warning(f"Primary API HTTP error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1 * (attempt + 1))
                continue
        except Exception as e:
            logging.warning(f"Primary API error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1 * (attempt + 1))
                continue
    
    logging.error("Primary API (alquran.cloud) failed after all retries")
    
    # Fallback API 1: Try alternative endpoint with retry
    for attempt in range(2):  # Fewer retries for fallback
        try:
            async with httpx.AsyncClient() as client:
                # Try getting the verse directly
                url = f"https://api.alquran.cloud/v1/ayah/{verse_number}"
                response = await client.get(url, timeout=15.0)
                response.raise_for_status()
                arabic_data = response.json()['data']
                
                # Get translation separately
                url_trans = f"https://api.alquran.cloud/v1/ayah/{verse_number}/{translation_code}"
                response_trans = await client.get(url_trans, timeout=15.0)
                response_trans.raise_for_status()
                trans_data = response_trans.json()['data']
                
                logging.info(f"Successfully fetched verse {verse_number} from fallback API 1")
                return {'source': 'alquran.cloud', 'data': [arabic_data, trans_data]}
        except Exception as e:
            logging.warning(f"Fallback API 1 error (attempt {attempt + 1}): {e}")
            if attempt < 1:
                await asyncio.sleep(2)
                continue
    
    # All APIs failed
    logging.error(f"All API attempts failed for verse {verse_number}")
    raise HTTPException(
        status_code=503, 
        detail="Unable to fetch verse at this time. Please check your internet connection and try again."
    )


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
