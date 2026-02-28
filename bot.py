import telebot
import json
import random
from telebot import types

TOKEN = '8733100208:AAGQ_UunyE1eiqPgURvGQJ7xoeBKJB341hY'
bot = telebot.TeleBot(TOKEN)

# Пайдаланушының тесттегі прогресін сақтау үшін
user_data = {}

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
    bot.reply_to(message, "🇰🇿 Сәлем! Саяхатта және күрделі тесттерден өт!", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🔎 Кездейсоқ орынды табу")
def send_random_place(message):
    places = load_locations()
    if not places: return
    target = random.choice(places)
    props = target.get('properties', {})
    name = props.get('name_kz', "Орын")
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    if props.get('gx_media_links'):
        markup.add(types.InlineKeyboardButton("📺 Бейнешолу", url=props['gx_media_links']))
    markup.add(types.InlineKeyboardButton("📖 Википедия", url=props.get('wiki_url', "")))
    markup.add(types.InlineKeyboardButton("📝 5 сұрақты тестті бастау", callback_data=f"start_quiz_{name}"))
    
    bot.send_message(message.chat.id, f"📍 *{name}*", parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('start_quiz_'))
def start_quiz(call):
    place_name = call.data.replace('start_quiz_', '')
    places = load_locations()
    target = next((p for p in places if p['properties'].get('name_kz') == place_name), None)
    
    if target and 'quiz' in target['properties']:
        user_data[call.from_user.id] = {
            'place': place_name,
            'current_q': 0,
            'score': 0,
            'questions': target['properties']['quiz']
        }
        send_question(call.message, call.from_user.id)

def send_question(message, user_id):
    data = user_data[user_id]
    q_idx = data['current_q']
    
    if q_idx < len(data['questions']):
        q = data['questions'][q_idx]
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for idx, opt in enumerate(q['options']):
            markup.add(types.InlineKeyboardButton(opt, callback_data=f"quiz_ans_{idx}"))
            
        bot.edit_message_text(f"❓ {q_idx + 1}-сұрақ:\n{q['question']}", 
                             message.chat.id, message.message_id, reply_markup=markup)
    else:
        score = data['score']
        total = len(data['questions'])
        bot.edit_message_text(f"🏁 Тест аяқталды!\nНәтижеңіз: {score}/{total}", 
                             message.chat.id, message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('quiz_ans_'))
def handle_answer(call):
    user_id = call.from_user.id
    if user_id not in user_data: return
    
    ans_idx = int(call.data.replace('quiz_ans_', ''))
    data = user_data[user_id]
    current_q = data['questions'][data['current_q']]
    
    if ans_idx == current_q['correct']:
        data['score'] += 1
        bot.answer_callback_query(call.id, "✅ Дұрыс!", show_alert=False)
    else:
        bot.answer_callback_query(call.id, f"❌ Қате! Дұрысы: {current_q['options'][current_q['correct']]}", show_alert=True)
        
    data['current_q'] += 1
    send_question(call.message, user_id)

bot.polling(none_stop=True)