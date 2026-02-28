@bot.message_handler(func=lambda message: message.text == "🔎 Найти случайное место")
def send_random_place(message):
    places = load_locations()
    if not places:
        bot.send_message(message.chat.id, "База данных пуста.")
        return

    target = random.choice(places)
    props = target.get('properties', {})
    geom = target.get('geometry', {})
    
    name = props.get('name', "Интересное место")
    desc = props.get('description', "Описание будет добавлено позже.")
    video_url = props.get('gx_media_links')

    # Отправка карты
    if geom and geom.get('type') == 'Point':
        coords = geom.get('coordinates')
        bot.send_location(message.chat.id, coords[1], coords[0])

    # Кнопка видео
    markup = types.InlineKeyboardMarkup()
    if video_url:
        markup.add(types.InlineKeyboardButton(f"📺 Видеообзор: {name}", url=video_url))
    
    # Отправка текста с названием и описанием
    bot.send_message(message.chat.id, f"📍 *{name}*\n\n{desc}", parse_mode='Markdown', reply_markup=markup)