import telebot
import json
import random
from telebot import types

# 1. БОТ ТОКЕНІ
TOKEN = '8733100208:AAGQ_UunyE1eiqPgURvGQJ7xoeBKJB341hY'
bot = telebot.TeleBot(TOKEN)

# Пайдаланушының тест прогресін сақтау үшін
user_data = {}

# 2. МӘЛІМЕТТЕРДІ ЖҮКТЕУ
def load_locations():
    try:
        # Файл атауы дұрыс болуы керек: kazakhstan_sites.geojson
        with open('kazakhstan_sites.geojson', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('features', [])
    except FileNotFoundError:
        print("Қате: kazakhstan_sites.geojson файлы табылмады!")
        return []
    except Exception as e:
        print(f"Файлды оқуда қате шықты: {e}")
        return []

# /start командасы
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔎 Кездейсоқ орынды табу"))
    welcome_text = (
        "🇰🇿 *Қазақстанның киелі жерлеріне қош келдіңіз!*\n\n"
        "Бұл бот арқылы сіз еліміздің тарихи нысандарымен танысып, "
        "олар туралы видео көріп, біліміңізді тест арқылы тексере аласыз."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=markup)

# "Кездейсоқ орынды табу" батырмасы
@bot.message_handler(func=lambda message: message.text == "🔎 Кездейсоқ орынды табу")
def send_random_place(message):
    places = load_locations()
    if not places:
        bot.send_message(message.chat.id, "Мәліметтер базасы уақытша қолжетімсіз.")
        return

    target = random.choice(places)
    props = target.get('properties', {})
    geom = target.get('geometry', {})
    
    name = props.get('name_kz', "Белгісіз нысан")
    video_url = props.get('gx_media_links', "").strip()
    wiki_url = props.get('wiki_url', "").strip()

    # Картаны жіберу (Telegram: latitude, longitude)
    if geom and 'coordinates' in geom:
        coords = geom['coordinates'] # GeoJSON-да: [lon, lat]
        bot.send_location(message.chat.id, coords[1], coords[0])

    # Инлайн батырмалар
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    if video_url:
        markup.add(types.InlineKeyboardButton("📺 Видео көру (YouTube)", url=video_url))
    
    if wiki_url:
        markup.add(types.InlineKeyboardButton("📖 Википедия мәліметі", url=wiki_url))
    
    # Тест бастау батырмасы (Нысан атауын ID ретінде жібереміз)
    markup.add(types.InlineKeyboardButton("📝 5 сұрақты тестті бастау", callback_data=f"quiz_{name[:15]}"))

    bot.send_message(message.chat.id, f"📍 *{name}*", parse_mode='Markdown', reply_markup=markup)

# --- ТЕСТ ЖҮЙЕСІ ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('quiz_'))
def start_quiz(call):
    place_prefix = call.data.replace('quiz_', '')
    places = load_locations()
    
    # Нысанды аты бойынша іздеу
    target = next((p for p in places if p['properties'].get('name_kz', '').startswith(place_prefix)), None)
    
    if target and 'quiz' in target['properties']:
        user_data[call.from_user.id] = {
            'questions': target['properties']['quiz'],
            'current_q': 0,
            'score': 0
        }
        send_question(call.message, call.from_user.id)
    else:
        bot.answer_callback_query(call.id, "Бұл нысан үшін тест әлі дайын емес.", show_alert=True)

def send_question(message, user_id):
    data = user_data[user_id]
    q_idx = data['current_q']
    questions = data['questions']
    
    if q_idx < len(questions):
        q = questions[q_idx]
        markup = types.InlineKeyboardMarkup(row_width=1)
        for idx, option in enumerate(q['options']):
            markup.add(types.InlineKeyboardButton(option, callback_data=f"ans_{idx}"))
            
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=f"❓ *{q_idx + 1}/{len(questions)} сұрақ:*\n\n{q['question']}",
            parse_mode='Markdown',
            reply_markup=markup
        )
    else:
        # Қорытынды
        score = data['score']
        total = len(questions)
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=f"🏁 *Тест аяқталды!*\n\nСіздің нәтижеңіз: *{score} / {total}*",
            parse_mode='Markdown'
        )
        del user_data[user_id]

@bot.callback_query_handler(func=lambda call: call.data.startswith('ans_'))
def handle_answer(call):
    user_id = call.from_user.id
    if user_id not in user_data:
        return

    ans_idx = int(call.data.replace('ans_', ''))
    data = user_data[user_id]
    current_q_data = data['questions'][data['current_q']]
    
    if ans_idx == current_q_data['correct']:
        data['score'] += 1
        bot.answer_callback_query(call.id, "✅ Дұрыс!")
    else:
        bot.answer_callback_query(call.id, "❌ Қате!", show_alert=False)
        
    data['current_q'] += 1
    send_question(call.message, user_id)

# 3. БОТТЫ ҚОСУ (Тұрақты жұмыс істеу режимі)
if __name__ == "__main__":
    print("Бот іске қосылды... Тексеру үшін Телеграмға кіріңіз.")
    # infinity_polling желі үзілсе де автоматты түрде қайта қосылады
    bot.infinity_polling(timeout=10, long_polling_timeout=5)