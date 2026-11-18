import time
import re
from google_play_scraper import reviews, Sort
from langdetect import detect, DetectorFactory
import openpyxl

# Set seed for deterministic language detection
DetectorFactory.seed = 0

print("Starting Scraper with Integrated Language Detection (Excel Output)...")

target_apps = [
    {"name": "MySejahtera", "package_id": "my.gov.onegovappstore.mysejahtera"},
    {"name": "UPUPocket", "package_id": "my.gov.onegovappstore.upupocket"},
    {"name": "MyUBAT", "package_id": "my.gov.onegovappstore.myubat"},
    {"name": "Volunteer Smartphone Patrol", "package_id": "my.gov.onegovappstore.rv2"},
    {"name": "ePayslip JANM", "package_id": "my.gov.onegovappstore.epayslipmobile"},
    {"name": "MySPR Semak", "package_id": "com.mysprsemak.spr"},
    {"name": "Vaccine Certificate Verifier", "package_id": "my.gov.onegovappstore.healthcertverifier"},
    {"name": "e-Lembaga Peperiksaan", "package_id": "my.gov.onegovappstore.elp"},
    {"name": "MyHRMIS Mobile", "package_id": "my.gov.jpa.eghrmis.mobile"},
    {"name": "Aplikasi MyLOT", "package_id": "my.gov.onegovappstore.mylot"}
]

# Localized Malay/Manglish indicators to assist langdetect
ms_keywords = set([
    'tak', 'takleh', 'xboleh', 'xda', 'xdapat', 'x', 'dapat', 'tolong', 'teruk', 
    'sangat', 'bagus', 'senang', 'susah', 'lambat', 'laju', 'gagal', 'buka', 
    'masuk', 'kecewa', 'kemaskini', 'guna', 'sistem', 'aplikasi', 'akaun', 
    'pantas', 'mudah', 'mantap', 'terbaik', 'sampah', 'bodoh', 'useless', 'harap'
])

def detect_real_language(text):
    if not text or len(str(text).strip()) < 3:
        return 'other'
    
    clean_text = str(text).lower()
    words = set(re.findall(r'\b\w+\b', clean_text))
    
    # Priority Rule: Malaysian slang / Malay keyword intercept
    if len(words.intersection(ms_keywords)) > 0:
        return 'ms'
    
    # Secondary Rule: langdetect engine
    try:
        lang = detect(clean_text)
        if lang in ['ms', 'id', 'tl', 'af']:  # Informal Malay often flags as id/tl/af
            return 'ms'
        elif lang == 'en':
            return 'en'
        else:
            return 'other'
    except:
        return 'other'

excel_file = "Datasets Ori.xlsx"
headers = ['App Name', 'User Name', 'Rating', 'Review Date', 'Review Text', 'Thumbs Up Count', 'App Version', 'Storefront_Lang', 'Detected_Lang']

# Create openpyxl Workbook
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Raw_Scraped_Data"

# Write headers
ws.append(headers)

# Style header row (Bold text)
for cell in ws[1]:
    cell.font = openpyxl.styles.Font(bold=True)

# Loop over apps
for app in target_apps:
    app_name = app["name"]
    app_id = app["package_id"]
    
    print(f"\n📥 Fetching reviews for: {app_name}")
    
    for sf_lang in ['en', 'ms']:
        try:
            fetched_reviews, _ = reviews(
                app_id,
                lang=sf_lang,
                country='my',
                sort=Sort.NEWEST,
                count=5000
            )
            
            print(f"   Downloaded {len(fetched_reviews)} raw reviews under storefront flag [{sf_lang.upper()}]...")
            
            for review in fetched_reviews:
                text_content = review.get('content', '')
                
                # Strip out non-printable control characters that Excel cannot store
                if text_content:
                    text_content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', str(text_content))
                
                # Real-time language detection on the review content
                real_lang = detect_real_language(text_content)
                
                # Format Review Date for Excel compatibility (string ISO or formatted string)
                review_date = review.get('at')
                if review_date:
                    review_date = review_date.strftime("%Y-%m-%d %H:%M:%S")
                
                # Append row directly to Excel worksheet
                ws.append([
                    app_name,
                    review.get('userName'),
                    review.get('score'),
                    review_date,
                    text_content,
                    review.get('thumbsUpCount'),
                    review.get('reviewCreatedVersion'),
                    sf_lang,     # Original parameter requested from Google API
                    real_lang    # Verified language via inline detection
                ])
                
            time.sleep(1.5) # Polite delay
            
        except Exception as e:
            print(f"   ❌ Error fetching [{sf_lang.upper()}] for {app_name}: {e}")

print(f"\n💾 Saving data into '{excel_file}'...")
wb.save(excel_file)

print(f"\n🎉 Integrated scraping and language detection complete! Output saved in '{excel_file}'.")