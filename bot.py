import telebot
import json
import random
from telebot import types

# Бот токені
TOKEN = '8733100208:AAGQ_UunyE1eiqPgURvGQJ7xoeBKJB341hY'
bot = telebot.TeleBot(TOKEN)

# Пайдаланушының тесттегі прогресін сақтау
user_data = {}

def load_locations():
    try:
        with open('kazakhstan_sites.geojson', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('features', [])
    except Exception as e:
        print(f"Файлды жүктеу қатесі: {e}")
        return []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔎 Кездейсоқ орынды табу"))
    bot.reply_to(message, "🇰🇿 Сәлем! Қазақстанның киелі жерлерін танып, 5 сұрақты тесттен өт!", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🔎 Кездейсоқ орынды табу")
def send_random_place(message):
    places = load_locations()
    if not places:
        bot.send_message(message.chat.id, "Мәліметтер базасы бос.")
        return

    target = random.choice(places)
    props = target.get('properties', {})
    geom = target.get('geometry', {})
    name = props.get('name_kz', "Орын")
    wiki = props.get('wiki_url', "https://kk.wikipedia.org")
    video = props.get('gx_media_links', "")

    # 1. Картаны жіберу
    if geom and geom.get('type') == 'Point':
        coords = geom.get('coordinates')
        try:
            bot.send_location(message.chat.id, coords[1], coords[0])
        except Exception as e:
            print(f"Карта жіберу қатесі: {e}")

    # 2. Батырмалар жасау
    markup = types.InlineKeyboardMarkup(row_width=1)
    if video:
        markup.add(types.InlineKeyboardButton("📺 Бейнешолуды көру", url=video.strip()))
    
    markup.add(types.InlineKeyboardButton("📖 Википедия мәліметі", url=wiki))
    
    # Callback_data қатесін болдырмау үшін нысан атын қысқартып жібереміз
    short_id = name[:10]
    markup.add(types.InlineKeyboardButton("📝 5 сұрақты тестті бастау", callback_data=f"sq_{short_id}"))

    bot.send_message(message.chat.id, f"📍 *{name}*\n\nТөмендегі батырмалар арқылы толық мәлімет алып, біліміңізді тексеріңіз!", parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('sq_'))
def start_quiz(call):
    short_id = call.data.replace('sq_', '')
    places = load_locations()
    target = next((p for p in places if p['properties'].get('name_kz', '').startswith(short_id)), None)
    
    if target and 'quiz' in target['properties']:
        user_data[call.from_user.id] = {
            'place_id': short_id,
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
            # Жауап батырмалары
            markup.add(types.InlineKeyboardButton(opt, callback_data=f"qa_{idx}"))
            
        bot.edit_message_text(f"❓ {q_idx + 1}-сұрақ:\n{q['question']}", 
                             message.chat.id, message.message_id, reply_markup=markup)
    else:
        score = data['score']
        bot.edit_message_text(f"🏁 Тест аяқталды!\nНәтижеңіз: {score}/5", 
                             message.chat.id, message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('qa_'))
def handle_answer(call):
    user_id = call.from_user.id
    if user_id not in user_data: return
    
    ans_idx = int(call.data.replace('qa_', ''))
    data = user_data[user_id]
    current_q = data['questions'][data['current_q']]
    
    if ans_idx == current_q['correct']:
        data['score'] += 1
        bot.answer_callback_query(call.id, "✅ Дұрыс!", show_alert=False)
    else:
        correct_val = current_q['options'][current_q['correct']]
        bot.answer_callback_query(call.id, f"❌ Қате! Дұрыс жауап: {correct_val}", show_alert=True)
        
    data['current_q'] += 1
    send_question(call.message, user_id)

if __name__ == "__main__":
    print("Бот іске қосылды...")
    bot.polling(none_stop=True)