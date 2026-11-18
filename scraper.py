import csv
from google_play_scraper import reviews, Sort

print("Starting High-Volume MySejahtera Scraper...")

# FIXED: Replaced 'oneos' with the correct 'onegovappstore' package ID
app_id = 'my.gov.onegovappstore.mysejahtera'
csv_file = "mysejahtera_reviews.csv"
headers = ['User Name', 'Rating', 'Review Date', 'Review Text', 'Thumbs Up Count', 'App Version']

try:
    print(f"📥 Pulling reviews for package: {app_id}")
    
    # Let's request a solid batch of 1,000 reviews
    fetched_reviews, _ = reviews(
        app_id,
        lang='en',         # Scrape English reviews first
        country='my',      # Target the Malaysian Google Play Store region
        sort=Sort.NEWEST,  # Sort to grab the most recent comments
        count=50000         
    )
    
    # Fallback check: If English lists are thin, auto-grab Bahasa Melayu reviews
    if len(fetched_reviews) == 0:
        print("⚠️ No English reviews found under this ID. Fetching with language parameter 'ms'...")
        fetched_reviews, _ = reviews(
            app_id,
            lang='ms',
            country='my',
            sort=Sort.NEWEST,
            count=50000
        )

    total_count = len(fetched_reviews)
    print(f"✅ Successfully downloaded {total_count} reviews!")

    if total_count > 0:
        print(f"💾 Writing data into '{csv_file}'...")
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            
            for review in fetched_reviews:
                writer.writerow([
                    review.get('userName'),
                    review.get('score'),
                    review.get('at'),
                    review.get('content'),
                    review.get('thumbsUpCount'),
                    review.get('reviewCreatedVersion')
                ])
        print("🎉 Export complete! Open 'mysejahtera_reviews.csv' to look at your data.")
    else:
        print("❌ Double check the network. Google Play returned 0 records.")

except Exception as e:
    print(f"❌ Scraping stopped due to an error: {e}")