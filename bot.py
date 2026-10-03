import os
import time
import random
import requests
from bs4 import BeautifulSoup
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TG_TOKEN = os.environ.get("TG_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Ошибка отправки в TG: {e}")

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Используем мобильную версию сайта (m.avito.ru), она часто лояльнее к парсерам
    AVITO_URL = "https://m.avito.ru/solikamsk/telefony/sotovye_telefony-asg-SgJ0KC5icg?cd=1&s=104"
    
    # Рандомные юзер-агенты реальных мобильных устройств
    USER_AGENTS = [
        "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1"
    ]

    HEADERS = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://m.avito.ru/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    print("Проверяю Авито...")
    
    # Создаем сессию, чтобы сохранять куки, как настоящий браузер
    session = requests.Session()
    
    # Делаем случайную задержку перед запросом, чтобы сбить антибот-алгоритмы
    time.sleep(random.uniform(1.5, 4.0))
    
    response = session.get(AVITO_URL, headers=HEADERS, timeout=15)
    print(f"Статус ответа Авито: {response.status_code}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        ads = soup.find_all('div', {'data-marker': 'item'})
        print(f"Найдено блоков объявлений: {len(ads)}")
        
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
            
            msg = f"*[Тест / Новое с Авито]*\n[{title}]({link})\n💰 Цена: *{price}*\n\n{ai_resp.text}"
            send_telegram(msg)
        else:
            send_telegram("⚠️ Авито отдал страницу, но объявлений на ней нет (возможно, Авито выдал капчу).")
    
    elif response.status_code == 429:
        send_telegram("❌ Авито всё еще блокирует сервер GitHub (Код 429: Слишком много запросов).")
    else:
        send_telegram(f"❌ Ошибка доступа к Авито, код: {response.status_code}")

except Exception as e:
    err_msg = f"❌ Ошибка в коде бота: {str(e)}"
    print(err_msg)
    if TG_TOKEN and TG_CHAT_ID:
        send_telegram(err_msg)
       if ads:
            ad = ads[0]
            title_tag = ad.find('h3', {'itemprop': 'name'})
            title = title_tag.text.strip() if title_tag else "Без названия"
            
            link_tag = ad.find('a', {'itemprop': 'url'})
            link = "https://www.avito.ru" + link_tag['href'] if link_tag else ""
            
            price_tag = ad.find('span', {'data-marker': 'item-price'})
            price = price_tag.text.strip() if price_tag else "Цена не указана"
            
            prompt = f"Оцени объявление с Авито: {title}, цена: {price}. Стоит ли брать? Ответь коротко в 2 предложениях."
            ai_resp = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            
            msg = f"*[Тест / Новое с Авито]*\n[{title}]({link})\n💰 Цена: *{price}*\n\n{ai_resp.text}"
            send_telegram(msg)
        else:
            send_telegram("⚠️ Бот запущен, но Авито не отдал блоки объявлений (возможно, изменилась верстка или сработала защита).")
    else:
        send_telegram(f"❌ Ошибка доступа к Авито, код: {response.status_code}")

except Exception as e:
    err_msg = f"❌ Ошибка в коде бота: {str(e)}"
    print(err_msg)
    if TG_TOKEN and TG_CHAT_ID:
        send_telegram(err_msg)
