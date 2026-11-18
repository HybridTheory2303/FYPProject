import re
import unicodedata
import pandas as pd
from lingua import Language, LanguageDetectorBuilder

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================
INPUT_EXCEL = "Cleaning - Copy.xlsx"
OUTPUT_EXCEL = "dataset_with_language_12cols.xlsx"
REVIEW_COLUMN = "Review Text"  # Change to match your exact column header

# ==============================================================================
# 2. INITIALIZE DETECTOR (Malay, Indonesian, English)
# ==============================================================================
detector = LanguageDetectorBuilder.from_languages(
    Language.MALAY, Language.INDONESIAN, Language.ENGLISH
).build()

MS_MARKERS = {'saya', 'aku', 'tak', 'x', 'yg', 'yang', 'untuk', 'utk', 'tapi', 'dah', 
              'boleh', 'nak', 'ni', 'tu', 'je', 'jee', 'sangat', 'sgt', 'bagus', 
              'mudah', 'susah', 'lambat', 'masuk', 'keluar', 'spi', 'sampai', 'tq'}
EN_MARKERS = {'the', 'is', 'are', 'was', 'and', 'but', 'good', 'bad', 'easy', 'slow', 
              'app', 'login', 'update', 'error', 'failed', 'please', 'thank', 'thanks', 
              'nice', 'great', 'friendly', 'user', 'done', 'ok', 'okay', 'no'}

def identify_review_language(text):
    if not isinstance(text, str) or not text.strip():
        return "Other"
    
    # Normalize Unicode stylized fonts ("ｍｕｄａｈ.." -> "mudah..")
    clean_text = unicodedata.normalize('NFKC', text).lower()
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # Emoji-only / numeric-only reviews -> 'Other'
    alpha_only = re.sub(r'[^a-z\s]', '', clean_text).strip()
    if len(alpha_only) < 2:
        return "Other"
    
    # Lexical Code-Switching check (Manglish)
    tokens = set(alpha_only.split())
    if len(tokens.intersection(MS_MARKERS)) > 0 and len(tokens.intersection(EN_MARKERS)) > 0:
        return "Code-Switched"
    
    # Detect language
    detected = detector.detect_language_of(alpha_only)
    if detected in [Language.MALAY, Language.INDONESIAN]:
        return "ms"
    elif detected == Language.ENGLISH:
        return "en"
    else:
        return "ms"

# ==============================================================================
# 3. PROCESS EXCEL & ADD 12TH COLUMN
# ==============================================================================
df = pd.read_excel(INPUT_EXCEL)
df["language_tag"] = df[REVIEW_COLUMN].apply(identify_review_language)
df.to_excel(OUTPUT_EXCEL, index=False)

print(f"Done! Saved {OUTPUT_EXCEL} with {len(df.columns)} columns.")
print(df["language_tag"].value_counts())