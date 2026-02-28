import telebot
import json
import random
from telebot import types

TOKEN = '8733100208:AAGQ_UunyE1eiqPgURvGQJ7xoeBKJB341hY'
bot = telebot.TeleBot(TOKEN)

def load_locations():
    try:
        with open('kazakhstan_sites.geojson', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('features', [])
    except Exception as e:
        print(f"Қате: {e}")
        return []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔎 Кездейсоқ орынды табу"))
    bot.reply_to(message, "🇰🇿 Сәлем! Киелі жерді таңдап, Википедияны оқы және тест тапсыр!", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🔎 Кездейсоқ орынды табу")
def send_random_place(message):
    places = load_locations()
    if not places: return

    target = random.choice(places)
    props = target.get('properties', {})
    geom = target.get('geometry', {})
    
    name = props.get('name_kz', "Орын")
    wiki_url = props.get('wiki_url', "https://kk.wikipedia.org")
    
    # Карта жіберу
    if geom and geom.get('type') == 'Point':
        coords = geom.get('coordinates')
        bot.send_location(message.chat.id, coords[1], coords[0])

    # Батырмалар: Видео, Википедия және Тест
    markup = types.InlineKeyboardMarkup(row_width=1)
    if props.get('gx_media_links'):
        markup.add(types.InlineKeyboardButton("📺 Бейнешолу", url=props['gx_media_links']))
    
    markup.add(types.InlineKeyboardButton("📖 Википедияда оқу", url=wiki_url))
    
    # Тест бастау батырмасы (callback дерегімен)
    test_btn = types.InlineKeyboardButton("📝 Тест тапсыру", callback_data=f"test_{name}")
    markup.add(test_btn)
    
    bot.send_message(message.chat.id, f"📍 *{name}*\n\nМәліметтермен танысып болсаңыз, тест тапсырып көріңіз!", parse_mode='Markdown', reply_markup=markup)

# Тест сұрақтарын өңдеу
@bot.callback_query_handler(func=lambda call: call.data.startswith('test_'))
def start_test(call):
    place_name = call.data.replace('test_', '')
    places = load_locations()
    
    # Сәйкес орынды және оның сұрағын табу
    target = next((p for p in places if p['properties'].get('name_kz') == place_name), None)
    
    if target and 'test' in target['properties']:
        test_data = target['properties']['test']
        question = test_data['question']
        options = test_data['options']
        correct = test_data['correct']
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        for idx, opt in enumerate(options):
            # Жауапты тексеру үшін индекс пен орын атын жібереміз
            callback_data = f"ans_{idx}_{place_name}"
            markup.add(types.InlineKeyboardButton(opt, callback_data=callback_data))
            
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                             text=f"❓ *Сұрақ:* {question}", reply_markup=markup, parse_mode='Markdown')

# Жауапты тексеру
@bot.callback_query_handler(func=lambda call: call.data.startswith('ans_'))
def check_answer(call):
    _, ans_idx, place_name = call.data.split('_')
    places = load_locations()
    target = next((p for p in places if p['properties'].get('name_kz') == place_name), None)
    
    if target:
        correct_idx = target['properties']['test']['correct']
        if int(ans_idx) == correct_idx:
            result = "✅ Дұрыс! Жарайсыз!"
        else:
            correct_text = target['properties']['test']['options'][correct_idx]
            result = f"❌ Қате. Дұрыс жауабы: {correct_text}"
            
        bot.answer_callback_query(call.id, result, show_alert=True)
        bot.send_message(call.message.chat.id, f"Саяхатты жалғастыру үшін батырманы басыңыз 👇")

if __name__ == "__main__":
    bot.polling(none_stop=True)