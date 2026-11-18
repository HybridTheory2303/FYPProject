import re
import unicodedata
import pandas as pd
from lingua import Language, LanguageDetectorBuilder

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================
INPUT_EXCEL = "Cleaning - Copy.xlsx"
OUTPUT_EXCEL = "dataset_with_language_13cols.xlsx"
REVIEW_COLUMN = "Review Text"  # Change to match your exact column header

# ==============================================================================
# 2. INITIALIZE DETECTOR (Malay, Indonesian, English)
# ==============================================================================
detector = LanguageDetectorBuilder.from_languages(
    Language.MALAY, Language.INDONESIAN, Language.ENGLISH
).build()

# Malaysian public sector app names to ignore during language scoring
APP_NAMES = r'\b(mydigital|myhrmis|mysejahtera|myjpj|hrmis|elp|pt3|mylot|myubat|upu|upupocket|vsp|vcp)\b'

MS_MARKERS = {'saya', 'aku', 'tak', 'x', 'yg', 'yang', 'untuk', 'utk', 'tapi', 'dah', 
              'boleh', 'nak', 'ni', 'tu', 'je', 'jee', 'sangat', 'sgt', 'bagus', 
              'mudah', 'susah', 'lambat', 'masuk', 'keluar', 'spi', 'sampai', 'tq',
              'kena', 'guna', 'daftar', 'kat', 'la', 'lah'}

EN_MARKERS = {'the', 'is', 'are', 'was', 'and', 'but', 'good', 'bad', 'easy', 'slow', 
              'app', 'login', 'update', 'error', 'failed', 'please', 'thank', 'thanks', 
              'nice', 'great', 'friendly', 'user', 'done', 'ok', 'okay', 'no',
              'uninstall', 'install', 'mobile', 'goodbye', 'download'}

def analyze_review_languages(text):
    """
    Returns a tuple: (language_tag, dominant_language)
    - language_tag: 'ms', 'en', 'Code-Switched', or 'Other'
    - dominant_language: 'ms', 'en', or 'Other' (shows majority language even in Code-Switched rows)
    """
    if not isinstance(text, str) or not text.strip():
        return ("Other", "Other")
    
    # Normalize Unicode stylized fonts ("ｍｕｄａｈ.." -> "mudah..")
    clean_text = unicodedata.normalize('NFKC', text).lower()
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # Emoji-only / numeric-only reviews -> 'Other'
    alpha_only = re.sub(r'[^a-z\s]', '', clean_text).strip()
    if len(alpha_only) < 2:
        return ("Other", "Other")
    
    # Strip Malaysian app names (e.g., mydigital, myhrmis) so 'my-' doesn't bias English score
    scoring_text = re.sub(APP_NAMES, ' ', alpha_only)
    scoring_text = re.sub(r'\s+', ' ', scoring_text).strip() or alpha_only
    
    # Compute confidence scores across Malay, Indonesian, and English
    confidences = detector.compute_language_confidence_values(scoring_text)
    
    # Combine Malay + Indonesian scores into a single 'ms' score
    ms_score = sum(c.value for c in confidences if c.language in [Language.MALAY, Language.INDONESIAN])
    en_score = sum(c.value for c in confidences if c.language == Language.ENGLISH)
    
    dominant = "ms" if ms_score >= en_score else "en"
    
    # Check for lexical Code-Switching (Manglish)
    tokens = set(alpha_only.split())
    if len(tokens.intersection(MS_MARKERS)) > 0 and len(tokens.intersection(EN_MARKERS)) > 0:
        return ("Code-Switched", dominant)
    
    return (dominant, dominant)

# ==============================================================================
# 3. PROCESS EXCEL & ADD 12TH AND 13TH COLUMNS
# ==============================================================================
df = pd.read_excel(INPUT_EXCEL)
df.columns = df.columns.str.strip()  # Clean any hidden header spaces

results = df[REVIEW_COLUMN].apply(analyze_review_languages)
df["language_tag"] = [r[0] for r in results]
df["dominant_language"] = [r[1] for r in results]

df.to_excel(OUTPUT_EXCEL, index=False)

print(f"Done! Saved {OUTPUT_EXCEL} with {len(df.columns)} columns.\n")
print("1. Overall Language Tag Breakdown:")
print(df["language_tag"].value_counts())
print("\n2. Dominant Language Inside Code-Switched Reviews:")
print(df[df["language_tag"] == "Code-Switched"]["dominant_language"].value_counts())