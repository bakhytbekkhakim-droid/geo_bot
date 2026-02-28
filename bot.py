@bot.message_handler(func=lambda message: message.text == "🔎 Найти случайное место")
def send_random_place(message):
    places = load_locations()
    if not places:
        bot.send_message(message.chat.id, "База данных пуста.")
        return

    # 1. Выбираем случайное место
    target = random.choice(places)
    props = target.get('properties', {})
    geom = target.get('geometry', {})
    
    # 2. Берем данные именно этого ВЫБРАННОГО места
    name = props.get('name') or "Интересное место"
    # Сначала ищем в gx_media_links, если нет - ищем в description
    video_url = props.get('gx_media_links') 
    
    if not video_url and 'description' in props:
        desc_val = str(props['description'])
        youtube_links = re.findall(r'(https?://(?:www\.)?youtube\.com/[^\s<>"]+|https?://youtu\.be/[^\s<>"]+)', desc_val)
        if youtube_links:
            video_url = youtube_links[0]

    # 3. Отправляем карту (если есть координаты)
    if geom and geom.get('type') == 'Point':
        coords = geom.get('coordinates')
        if coords and len(coords) >= 2:
            bot.send_location(message.chat.id, coords[1], coords[0])

    # 4. Создаем кнопку ТОЛЬКО с актуальной ссылкой
    markup = types.InlineKeyboardMarkup()
    if video_url:
        # Очищаем ссылку от лишних кавычек
        clean_url = video_url.split('"')[0].split("'")[0].split("<")[0]
        markup.add(types.InlineKeyboardButton(f"📺 Видео: {name}", url=clean_url))
    
    bot.send_message(message.chat.id, f"📍 *{name}*", parse_mode='Markdown', reply_markup=markup)