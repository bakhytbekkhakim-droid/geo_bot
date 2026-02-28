import telebot
import json
import random
from telebot import types
import re

# 1. Ботты инициализациялау
TOKEN = '8733100208:AAGQ_UunyE1eiqPgURvGQJ7xoeBKJB341hY'
bot = telebot.TeleBot(TOKEN)

# 2. Мәліметтерді жүктеу функциясы
def load_locations():
    try:
        with open('kazakhstan_sites.geojson', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('features', [])
    except Exception as e:
        print(f"Қате: {e}")
        return []

# 3. /start командасы
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔎 Кездейсоқ орынды табу"))
    welcome_text = (
        "🇰🇿 Сәлем! Мен Қазақстанның киелі жерлері бойынша жолбасшымын.\n\n"
        "Төмендегі батырманы басып, қызықты орынды, оның картасы мен бейнешолуын ал!"
    )
    bot.reply_to(message, welcome_text, reply_markup=markup)

# 4. Орынды іздеу логикасы
@bot.message_handler(func=lambda message: message.text == "🔎 Кездейсоқ орынды табу")
def send_random_place(message):
    places = load_locations()
    if not places:
        bot.send_message(message.chat.id, "Мәліметтер базасы бос.")
        return

    target = random.choice(places)
    props = target.get('properties', {})
    geom = target.get('geometry', {})
    
    name = props.get('name_kz') or props.get('name', "Қызықты орын")
    desc = props.get('description_kz') or props.get('description', "Сипаттама жақын арада қосылады.")
    video_url = props.get('gx_media_links')

    # Картаны жіберу
    has_map = False
    if geom and geom.get('type') == 'Point':
        coords = geom.get('coordinates')
        if coords and len(coords) >= 2:
            try:
                bot.send_location(message.chat.id, coords[1], coords[0])
                has_map = True
            except:
                pass

    # Бейнешолу батырмасы
    markup = types.InlineKeyboardMarkup()
    if video_url:
        markup.add(types.InlineKeyboardButton(f"📺 Бейнешолуды көру: {name}", url=video_url))
    
    status_text = f"📍 *{name}*\n\n{desc}"
    if not has_map:
        status_text += "\n\n_(Карта уақытша қолжетімсіз)_"

    bot.send_message(message.chat.id, status_text, parse_mode='Markdown', reply_markup=markup)

# 5. Іске қосу
if __name__ == "__main__":
    print("--- БОТ ІСКЕ ҚОСЫЛДЫ ---")
    bot.polling(none_stop=True)