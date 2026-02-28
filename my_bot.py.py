import telebot
from telebot import types
import json
import random

# Ваш токен
TOKEN = '8733100208:AAGQ_UunyE1eiqPgURvGQJ7xoeBKJB341hY'
bot = telebot.TeleBot(TOKEN)

# Функция для чтения локаций из файла
def load_locations(filename='kazakhstan_sites.geojson'):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # ПЕЧАТАЕМ В ТЕРМИНАЛ СВОЙСТВА ПЕРВОГО ОБЪЕКТА (чтобы найти, где спрятано название)
    if data.get('features'):
        print("--- ДИАГНОСТИКА ---")
        print("Свойства из файла:", data['features'][0].get('properties'))
        print("-------------------")
        
    places = []
    for feature in data.get('features', []):
        properties = feature.get('properties', {})
        
        # Пробуем разные популярные варианты ключей для названия
        name = properties.get('name', properties.get('Name', properties.get('title', 'Неизвестная локация'))) 
        
        geometry = feature.get('geometry', {})
        if geometry and geometry.get('type') == 'Point':
            coordinates = geometry.get('coordinates', [0, 0])
            places.append({
                'name': name,
                'lon': coordinates[0],
                'lat': coordinates[1]
            })
    return places

places_list = load_locations()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📍 Случайная локация")
    markup.add(btn1)
    
    bot.send_message(
        message.chat.id, 
        "Сәлем! Нажми на кнопку ниже, и я покажу тебе случайную интересную локацию в Казахстане 🇰🇿",
        reply_markup=markup
    )

@bot.message_handler(commands=['place'])
@bot.message_handler(func=lambda message: message.text == "📍 Случайная локация")
def send_random_place(message):
    if not places_list:
        bot.send_message(message.chat.id, "Упс, список локаций пуст или не загрузился.")
        return
    
    random_place = random.choice(places_list)
    
    bot.send_message(message.chat.id, f"Отправляемся сюда: {random_place['name']}")
    bot.send_location(
        message.chat.id, 
        latitude=random_place['lat'], 
        longitude=random_place['lon']
    )

if __name__ == '__main__':
    print("Бот запущен и готов к работе! Жду сообщений...")
    bot.polling(none_stop=True)