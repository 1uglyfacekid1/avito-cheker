import os
import time
import requests
from bs4 import BeautifulSoup
from google import genai

# Подтягиваем ключи из секретов GitHub Actions
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TG_TOKEN = os.environ.get("TG_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

client = genai.Client(api_key=GEMINI_API_KEY)

# Ссылка на нужный поиск Авито (можешь поменять под свой город/категорию)
AVITO_URL = "https://www.avito.ru/solikamsk/telefony/sotovye_telefony-asg-SgJ0KC5icg?cd=1&s=104"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9",
}

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Ошибка отправки в TG: {e}")

def ask_gemini(title, price):
    prompt = f"""
    Оцени объявление с Авито:
    Название: {title}
    Цена: {price}
    
    Стоит ли брать? Выгодная ли это цена или подозрительный хлам? 
    Напиши короткий вердикт в 2 предложениях. Начни с "🔥 ВЫГОДНО:", "⚠️ ПОДОЗРИТЕЛЬНО:" или "❌ ДОРОГО:".
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Анализ недоступен: {e}"

def check_ads():
    print("🔍 Проверяю Авито...")
    try:
        response = requests.get(AVITO_URL, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"Авито отдал код ошибки: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        ads = soup.find_all('div', {'data-marker': 'item'})
        
        # Берем самое первое (самое свежее) объявление для теста
        if ads:
            ad = ads[0]
            title_tag = ad.find('h3', {'itemprop': 'name'})
            title = title_tag.text.strip() if title_tag else "Без названия"
            
            link_tag = ad.find('a', {'itemprop': 'url'})
            link = "https://www.avito.ru" + link_tag['href'] if link_tag else ""
            
            price_tag = ad.find('span', {'data-marker': 'item-price'})
            price = price_tag.text.strip() if price_tag else "Цена не указана"
            
            print( найден: {title} — {price} )
            verdict = ask_gemini(title, price)
            
            msg = f"*[Тест / Новое с Авито]*\n[{title}]({link})\n💰 Цена: *{price}*\n\n{verdict}"
            send_telegram(msg)

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    ch
  eck_ads()
