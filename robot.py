import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from supabase import create_client

# Connect to Gemini AI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

# Connect to your Database
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

def find_scholarships():
    # The Robot visits a big scholarship site
    url = "https://www.scholarshipsads.com/category/tags/international-scholarships/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # It finds 5 newest scholarships
    items = soup.select(".post-column")[:5]
    
    for item in items:
        title = item.select_one(".post-title").text.strip()
        link = item.select_one("a")["href"]
        
        # GEMINI AI reads the title and decides the level
        prompt = f"Extract education level (Undergraduate, Masters, or PhD) and Country from this title: {title}. Reply in this format: Level | Country"
        ai_response = model.generate_content(prompt).text
        level, country = ai_response.split("|")

        # Save to your website database
        supabase.table("scholarships").upsert({
            "title": title,
            "link": link,
            "level": level.strip(),
            "country": country.strip()
        }).execute()
        print(f"Gemini posted: {title}")

if __name__ == "__main__":
    find_scholarships()
