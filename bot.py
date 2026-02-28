import telebot
import json
import random
from telebot import types
import re

# 1. Настройка бота с вашим актуальным токеном
TOKEN = '8733100208:AAGQ_UunyE1eiqPgURvGQJ7xoeBKJB341hY'
bot = telebot.TeleBot(TOKEN)

# 2. Функция загрузки данных из GeoJSON
def load_locations():
    try:
        with open('kazakhstan_sites.geojson', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('features', [])
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return []

# 3. Приветственное сообщение
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔎 Найти случайное место"))
    
    welcome_text = (
        "🇰🇿 Привет! Я путеводитель по историческим местам.\n\n"
        "Нажми кнопку, и я пришлю тебе случайную локацию с картой и видеообзором!"
    )
    bot.reply_to(message, welcome_text, reply_markup=markup)

# 4. Основная логика (с проверкой координат и видео)
@bot.message_handler(func=lambda message: message.text == "🔎 Найти случайное место")
def send_random_place(message):
    places = load_locations()
    
    if not places:
        bot.send_message(message.chat.id, "❌ База данных пуста.")
        return

    # Выбираем случайное место
    target = random.choice(places)
    props = target.get('properties', {})
    geom = target.get('geometry', {})
    
    # Определяем название (поддерживаем разные форматы имен)
    name = props.get('name') or props.get('Name') or "Интересное место"
    
    # --- БЛОК ВИДЕО ---
    video_url = props.get('gx_media_links')
    if not video_url and 'description' in props:
        desc_data = props['description']
        text_to_search = str(desc_data['value']) if isinstance(desc_data, dict) else str(desc_data)
        # Ищем YouTube ссылки в тексте
        youtube_links = re.findall(r'(https?://(?:www\.)?youtube\.com/[^\s<>"]+|https?://youtu\.be/[^\s<>"]+)', text_to_search)
        if youtube_links:
            video_url = youtube_links[0]

    # --- БЛОК КАРТЫ (Исправленный) ---
    has_map = False
    if geom and geom.get('type') == 'Point':
        coords = geom.get('coordinates')
        if coords and len(coords) >= 2:
            try:
                # В GeoJSON: [долгота, широта]. В Telegram: (широта, долгота)
                bot.send_location(message.chat.id, coords[1], coords[0])
                has_map = True
            except Exception as e:
                print(f"Ошибка отправки координат: {e}")

    # --- ОТПРАВКА ТЕКСТА И КНОПКИ ---
    markup = types.InlineKeyboardMarkup()
    if video_url:
        # Очищаем ссылку от лишних символов HTML
        clean_url = video_url.split('"')[0].split("'")[0]
        markup.add(types.InlineKeyboardButton("📺 Смотреть видеообзор", url=clean_url))
    
    status_msg = f"📍 *{name}*"
    if not has_map:
        status_msg += "\n\n_(Координаты для этого места временно отсутствуют)_"
        
    bot.send_message(message.chat.id, status_msg, parse_mode='Markdown', reply_markup=markup)

# 5. Запуск
if __name__ == "__main__":
    print("--- БОТ ЗАПУЩЕН ---")
    bot.polling(none_stop=True)