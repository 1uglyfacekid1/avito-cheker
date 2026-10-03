import os
import requests
from bs4 import BeautifulSoup
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TG_TOKEN = os.environ.get("TG_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

def send_tg(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload, timeout=10)

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Мобильная версия Авито
    url = "https://m.avito.ru/solikamsk/telefony/sotovye_telefony-asg-SgJ0KC5icg?cd=1&s=104"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9",
    }
    
    resp = requests.get(url, headers=headers, timeout=15)
    
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        ads = soup.find_all('div', {'data-marker': 'item'})
        
        if ads:
            ad = ads[0]
            title_tag = ad.find('h3', {'itemprop': 'name'})
            title = title_tag.text.strip() if title_tag else "Без названия"
            
            link_tag = ad.find('a')
            link = "https://m.avito.ru" + link_tag['href'] if link_tag else ""
            
            price_tag = ad.find('span', {'data-marker': 'item-price'})
            price = price_tag.text.strip() if price_tag else "Цена не указана"
            
            prompt = f"Оцени объявление с Авито: {title}, цена: {price}. Стоит ли брать? Ответь коротко в 2 предложениях."
            ai_resp = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            
            send_tg(f"*[Тест Авито]*\n[{title}]({link})\n💰 Цена: *{price}*\n\n{ai_resp.text}")
        else:
            send_tg("⚠️ Страница загрузилась, но объявлений нет (возможно, Авито включил капчу).")
    
    elif resp.status_code == 429:
        send_tg("❌ Авито блокирует сервер (Код 429: Слишком много запросов).")
    
    else:
        send_tg(f"❌ Ошибка доступа к Авито, код: {resp.status_code}")

except Exception as e:
    send_tg(f"❌ Ошибка в коде бота: {str(e)}")
