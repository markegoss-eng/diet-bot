import telebot
import os
import time
import traceback
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise ValueError("❌ TOKEN не задан! Добавьте переменную окружения.")

bot = telebot.TeleBot(TOKEN)
user_data = {}

# ===== НАСТРОЙКИ =====
CHANNEL_LINK = "https://t.me/markpetrovskychannel"

# ===== КНОПКИ =====
def gender_keyboard():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(KeyboardButton("Мужской"), KeyboardButton("Женский"))
    return markup

def activity_keyboard():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        KeyboardButton("Минимальная (сидячая работа)"),
        KeyboardButton("Низкая (1-2 тренировки)"),
        KeyboardButton("Средняя (3-4 тренировки)"),
        KeyboardButton("Высокая (5-6 тренировок)")
    )
    return markup

def goal_keyboard():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        KeyboardButton("🔥 Снижение веса"),
        KeyboardButton("💪 Набор массы"),
        KeyboardButton("🔄 Рекомпозиция")
    )
    return markup

def friend_keyboard():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(KeyboardButton("👥 Рассчитать для близкого человека"))
    return markup

# ===== КОММЕНТАРИИ =====
COMMENTS = {
    "calories": {
        "Снижение веса": {
            "Мужской": "Меньше еды — жир уходит. Но если урежешь слишком сильно — организм затормозит, и вес встанет.",
            "Женский": "Дефицит мягкий, чтобы жир уходил, а ты не срывалась. Это комфортный темп."
        },
        "Набор массы": {
            "Мужской": "Много, но без этого мышцы не растут. Держи этот объём, чтобы набирать сухую массу, а не просто жир.",
            "Женский": "Набор без жесткого перебора. Мышцы будут расти, а жир не будет накапливаться."
        },
        "Рекомпозиция": {
            "Мужской": "Никакого дефицита. Вес может стоять на месте — это нормально. Твоё тело будет менять форму за счёт тренировок.",
            "Женский": "Никакого дефицита. Вес может стоять на месте — это нормально. Твоё тело будет менять форму за счёт тренировок, а не голодовки."
        }
    },
    "protein": {
        "Снижение веса": {
            "Мужской": "Если есть меньше белка — мышцы начнут «сыпаться», а жир останется. Белок защищает твоё тело во время дефицита.",
            "Женский": "Меньше белка — мышцы уходят, а жир остаётся. Белок защищает твоё тело во время дефицита."
        },
        "Набор массы": {
            "Мужской": "Это твой фундамент. Меньше белка — мышцы будут восстанавливаться дольше, а прогресс встанет. Акцент на курицу, творог и яйца.",
            "Женский": "Строительный материал для мышц. На наборе без него никуда — мышцы не будут расти даже с большим количеством еды."
        },
        "Рекомпозиция": {
            "Мужской": "Белок на максимуме, чтобы ты одновременно худел и строил мышцы. Не снижай.",
            "Женский": "Твой главный инструмент. При рекомпозиции белок идёт на восстановление мышц и помогает убирать жир даже без дефицита. Не снижай!"
        }
    },
    "fat": {
        "Снижение веса": {
            "Мужской": "Опустишь жиры ниже — тестостерон упадёт, и энергия будет на нуле. Это твой минимум.",
            "Женский": "Жиры — это твои гормоны и красивая кожа. На дефиците они защищают цикл и волосы."
        },
        "Набор массы": {
            "Мужской": "Жиры — это твой тестостерон. Опустишь ниже — гормоны скажут «спасибо, но мы уходим». Это твой минимум для мужского здоровья.",
            "Женский": "Жиры важны для женских гормонов и красивой кожи. Не занижай их, даже если кажется, что это много."
        },
        "Рекомпозиция": {
            "Мужской": "Жиры — это энергия и гормоны. На рекомпозиции они помогают телу перестраиваться без стресса.",
            "Женский": "Жиры — это твои гормоны и красивая кожа. На рекомпозиции они работают на тебя. Не занижай эту цифру, даже если кажется, что много."
        }
    },
    "carbs": {
        "Снижение веса": {
            "Мужской": "Меньше сладкого и мучного — быстрее уходит жир. Но полностью убирать нельзя, иначе сорвёшься.",
            "Женский": "Девушки часто боятся углеводов, но без них энергия падает. Эти углеводы — твои союзники, а не враги."
        },
        "Набор массы": {
            "Мужской": "Твоё топливо для тяжёлых тренировок. Если будешь их бояться — не будет сил жестко тренить. Ешь гречку, рис и макароны.",
            "Женский": "Углеводы — это энергия для тренировок и хорошего настроения. С ними ты будешь тренироваться ярче, а не через силу."
        },
        "Рекомпозиция": {
            "Мужской": "Топливо для тренировок. На рекомпозиции углеводы помогают держать интенсивность и не выгорать.",
            "Женский": "Энергия для тренировок и настроения. Углеводы помогают держать интенсивность, чтобы ты могла тренироваться в кайф, а не через силу."
        }
    }
}

# ===== ОБРАБОТЧИКИ =====
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    user_data[user_id] = {"self": {}, "friend": {}}
    bot.send_message(
        user_id,
        "👋 Привет! Я помогу рассчитать норму БЖУ.\n\n"
        "Сначала ответь на вопросы.\n"
        "Сколько тебе лет? (напиши цифру)"
    )
    bot.register_next_step_handler(message, get_age_self)

def get_age_self(message):
    user_id = message.chat.id
    try:
        age = int(message.text)
        if age < 10 or age > 100:
            bot.send_message(user_id, "❌ Введи реальный возраст (от 10 до 100)")
            bot.register_next_step_handler(message, get_age_self)
            return
        user_data[user_id]["self"]['age'] = age
        bot.send_message(user_id, "📏 Теперь укажи свой рост в сантиметрах (например, 175)")
        bot.register_next_step_handler(message, get_height_self)
    except:
        bot.send_message(user_id, "❌ Нужно ввести число!")
        bot.register_next_step_handler(message, get_age_self)

def get_height_self(message):
    user_id = message.chat.id
    try:
        height = int(message.text)
        if height < 100 or height > 250:
            bot.send_message(user_id, "❌ Введи реальный рост (от 100 до 250 см)")
            bot.register_next_step_handler(message, get_height_self)
            return
        user_data[user_id]["self"]['height'] = height
        bot.send_message(user_id, "⚖️ Сколько ты весишь? (в килограммах)")
        bot.register_next_step_handler(message, get_weight_self)
    except:
        bot.send_message(user_id, "❌ Нужно ввести число!")
        bot.register_next_step_handler(message, get_height_self)

def get_weight_self(message):
    user_id = message.chat.id
    try:
        weight = int(message.text)
        if weight < 30 or weight > 300:
            bot.send_message(user_id, "❌ Введи реальный вес (от 30 до 300 кг)")
            bot.register_next_step_handler(message, get_weight_self)
            return
        user_data[user_id]["self"]['weight'] = weight
        bot.send_message(user_id, "🧑 Выбери свой пол:", reply_markup=gender_keyboard())
        bot.register_next_step_handler(message, get_gender_self)
    except:
        bot.send_message(user_id, "❌ Нужно ввести число!")
        bot.register_next_step_handler(message, get_weight_self)

def get_gender_self(message):
    user_id = message.chat.id
    if message.text in ["Мужской", "Женский"]:
        user_data[user_id]["self"]['gender'] = message.text
        bot.send_message(
            user_id,
            "🏃 Теперь выбери уровень физической активности:",
            reply_markup=activity_keyboard()
        )
        bot.register_next_step_handler(message, get_activity_self)
    else:
        bot.send_message(user_id, "❌ Нажми на кнопку!")
        bot.register_next_step_handler(message, get_gender_self)

def get_activity_self(message):
    user_id = message.chat.id
    activity_levels = {
        "Минимальная (сидячая работа)": 1.2,
        "Низкая (1-2 тренировки)": 1.3,
        "Средняя (3-4 тренировки)": 1.4,
        "Высокая (5-6 тренировок)": 1.5
    }
    if message.text in activity_levels:
        user_data[user_id]["self"]['activity'] = activity_levels[message.text]
        bot.send_message(
            user_id,
            "🎯 Теперь выбери свою цель:",
            reply_markup=goal_keyboard()
        )
        bot.register_next_step_handler(message, get_goal_self)
    else:
        bot.send_message(user_id, "❌ Нажми на кнопку!")
        bot.register_next_step_handler(message, get_activity_self)

def get_goal_self(message):
    user_id = message.chat.id
    if message.text in ["🔥 Снижение веса", "💪 Набор массы", "🔄 Рекомпозиция"]:
        user_data[user_id]["self"]['goal'] = message.text
        send_photo_self(message)
    else:
        bot.send_message(user_id, "❌ Нажми на кнопку!")
        bot.register_next_step_handler(message, get_goal_self)

def send_photo_self(message):
    user_id = message.chat.id
    gender = user_data[user_id]["self"]['gender']
    file_path = "photos/male_body_fat_chart.jpg" if gender == "Мужской" else "photos/female_body_fat_chart.jpg"
    
    try:
        with open(file_path, 'rb') as photo:
            bot.send_photo(
                user_id,
                photo,
                caption=(
                    "📸 **Оцени свой процент жира**\n\n"
                    "Напиши **одним числом** процент, который подходит тебе больше всего.\n"
                    "Например: 15, 20 или 25\n\n"
                    "✏️ Напиши число в чат:"
                ),
                parse_mode='Markdown'
            )
    except:
        bot.send_message(user_id, "⚠️ Фото не найдено. Напиши свой процент жира числом (например, 15)")
    
    bot.register_next_step_handler(message, get_body_fat_self)

def get_body_fat_self(message):
    user_id = message.chat.id
    try:
        fat_percent = float(message.text)
        if fat_percent < 3 or fat_percent > 60:
            bot.send_message(user_id, "❌ Процент должен быть от 3 до 60. Попробуй еще раз.")
            bot.register_next_step_handler(message, get_body_fat_self)
            return
        user_data[user_id]["self"]['body_fat'] = fat_percent
        show_result(message, "self", "📊 **ТВОЯ НОРМА НА ДЕНЬ**")
    except:
        bot.send_message(user_id, "❌ Введи число! Попробуй еще раз.")
        bot.register_next_step_handler(message, get_body_fat_self)

# ===== АНКЕТА ДЛЯ БЛИЗКОГО =====
def get_age_friend(message):
    user_id = message.chat.id
    try:
        age = int(message.text)
        if age < 10 or age > 100:
            bot.send_message(user_id, "❌ Введи реальный возраст (от 10 до 100)")
            bot.register_next_step_handler(message, get_age_friend)
            return
        user_data[user_id]["friend"]['age'] = age
        bot.send_message(user_id, "📏 Теперь укажи рост в сантиметрах (например, 175)")
        bot.register_next_step_handler(message, get_height_friend)
    except:
        bot.send_message(user_id, "❌ Нужно ввести число!")
        bot.register_next_step_handler(message, get_age_friend)

def get_height_friend(message):
    user_id = message.chat.id
    try:
        height = int(message.text)
        if height < 100 or height > 250:
            bot.send_message(user_id, "❌ Введи реальный рост (от 100 до 250 см)")
            bot.register_next_step_handler(message, get_height_friend)
            return
        user_data[user_id]["friend"]['height'] = height
        bot.send_message(user_id, "⚖️ Какой вес? (в килограммах)")
        bot.register_next_step_handler(message, get_weight_friend)
    except:
        bot.send_message(user_id, "❌ Нужно ввести число!")
        bot.register_next_step_handler(message, get_height_friend)

def get_weight_friend(message):
    user_id = message.chat.id
    try:
        weight = int(message.text)
        if weight < 30 or weight > 300:
            bot.send_message(user_id, "❌ Введи реальный вес (от 30 до 300 кг)")
            bot.register_next_step_handler(message, get_weight_friend)
            return
        user_data[user_id]["friend"]['weight'] = weight
        bot.send_message(user_id, "🧑 Выбери пол:", reply_markup=gender_keyboard())
        bot.register_next_step_handler(message, get_gender_friend)
    except:
        bot.send_message(user_id, "❌ Нужно ввести число!")
        bot.register_next_step_handler(message, get_weight_friend)

def get_gender_friend(message):
    user_id = message.chat.id
    if message.text in ["Мужской", "Женский"]:
        user_data[user_id]["friend"]['gender'] = message.text
        bot.send_message(
            user_id,
            "🏃 Теперь выбери уровень физической активности:",
            reply_markup=activity_keyboard()
        )
        bot.register_next_step_handler(message, get_activity_friend)
    else:
        bot.send_message(user_id, "❌ Нажми на кнопку!")
        bot.register_next_step_handler(message, get_gender_friend)

def get_activity_friend(message):
    user_id = message.chat.id
    activity_levels = {
        "Минимальная (сидячая работа)": 1.2,
        "Низкая (1-2 тренировки)": 1.3,
        "Средняя (3-4 тренировки)": 1.4,
        "Высокая (5-6 тренировок)": 1.5
    }
    if message.text in activity_levels:
        user_data[user_id]["friend"]['activity'] = activity_levels[message.text]
        bot.send_message(
            user_id,
            "🎯 Теперь выбери цель:",
            reply_markup=goal_keyboard()
        )
        bot.register_next_step_handler(message, get_goal_friend)
    else:
        bot.send_message(user_id, "❌ Нажми на кнопку!")
        bot.register_next_step_handler(message, get_activity_friend)

def get_goal_friend(message):
    user_id = message.chat.id
    if message.text in ["🔥 Снижение веса", "💪 Набор массы", "🔄 Рекомпозиция"]:
        user_data[user_id]["friend"]['goal'] = message.text
        send_photo_friend(message)
    else:
        bot.send_message(user_id, "❌ Нажми на кнопку!")
        bot.register_next_step_handler(message, get_goal_friend)

def send_photo_friend(message):
    user_id = message.chat.id
    gender = user_data[user_id]["friend"]['gender']
    file_path = "photos/male_body_fat_chart.jpg" if gender == "Мужской" else "photos/female_body_fat_chart.jpg"
    
    try:
        with open(file_path, 'rb') as photo:
            bot.send_photo(
                user_id,
                photo,
                caption=(
                    "📸 **Оцени процент жира**\n\n"
                    "Напиши **одним числом** процент, который подходит ему/ей больше всего.\n"
                    "Например: 15, 20 или 25\n\n"
                    "✏️ Напиши число в чат:"
                ),
                parse_mode='Markdown'
            )
    except:
        bot.send_message(user_id, "⚠️ Фото не найдено. Напиши процент жира числом (например, 15)")
    
    bot.register_next_step_handler(message, get_body_fat_friend)

def get_body_fat_friend(message):
    user_id = message.chat.id
    try:
        fat_percent = float(message.text)
        if fat_percent < 3 or fat_percent > 60:
            bot.send_message(user_id, "❌ Процент должен быть от 3 до 60. Попробуй еще раз.")
            bot.register_next_step_handler(message, get_body_fat_friend)
            return
        user_data[user_id]["friend"]['body_fat'] = fat_percent
        show_result(message, "friend", "📊 **НОРМА**")
    except:
        bot.send_message(user_id, "❌ Введи число! Попробуй еще раз.")
        bot.register_next_step_handler(message, get_body_fat_friend)

# ===== РАСЧЁТ =====
def show_result(message, person, title):
    user_id = message.chat.id
    data = user_data[user_id][person]
    
    weight = data['weight']
    goal = data['goal']
    gender = data['gender']
    body_fat = data['body_fat'] / 100
    lean_mass = weight * (1 - body_fat)
    
    bmr = 370 + (21.6 * lean_mass)
    calories = bmr * data['activity']
    
    goal_text = ""
    adjustment_text = ""
    
    if goal == "🔥 Снижение веса":
        if weight > 80:
            calories -= 500
            adjustment_text = "Дефицит: 500 ккал"
        elif 70 <= weight <= 80:
            calories -= 400
            adjustment_text = "Дефицит: 400 ккал"
        else:
            calories -= 300
            adjustment_text = "Дефицит: 300 ккал"
        goal_text = "🔥 Снижение веса"
    
    elif goal == "💪 Набор массы":
        if weight < 70:
            calories += 500
            adjustment_text = "Профицит: 500 ккал"
        elif 70 <= weight <= 80:
            calories += 300
            adjustment_text = "Профицит: 300 ккал"
        else:
            calories += 200
            adjustment_text = "Профицит: 200 ккал"
        goal_text = "💪 Набор массы"
    
    else:
        goal_text = "🔄 Рекомпозиция"
        adjustment_text = "Без дефицита/профицита"
    
    if goal == "🔥 Снижение веса":
        protein_per_kg = 2.0
    elif goal == "💪 Набор массы":
        protein_per_kg = 1.8
    else:
        protein_per_kg = 2.2
    
    protein_grams = weight * protein_per_kg
    
    if (data['body_fat'] / 100) > 0.35:
        max_protein = lean_mass * 2.2
        if protein_grams > max_protein:
            protein_grams = max_protein
    
    if protein_grams > 220:
        protein_grams = 220
    
    protein_cal = protein_grams * 4
    
    fat_cal = calories * 0.3
    fat_grams = fat_cal / 9
    max_fat = weight * 1
    if fat_grams > max_fat:
        fat_grams = max_fat
        fat_cal = fat_grams * 9
    
    carbs_cal = calories - protein_cal - fat_cal
    carbs_grams = carbs_cal / 4
    
    goal_key = goal.replace("🔥 ", "").replace("💪 ", "").replace("🔄 ", "")
    comment_cal = COMMENTS["calories"][goal_key][gender]
    comment_protein = COMMENTS["protein"][goal_key][gender]
    comment_fat = COMMENTS["fat"][goal_key][gender]
    comment_carbs = COMMENTS["carbs"][goal_key][gender]
    
    answer = (
        f"{title}\n\n"
        f"🎯 Цель: {goal_text}\n"
        f"📊 {adjustment_text}\n"
        f"📉 Процент жира: {round(data['body_fat'])}%\n\n"
        f"🔥 **Калории:** {round(calories)} ккал\n"
        f"💡 {comment_cal}\n\n"
        f"🥩 **Белки:** {round(protein_grams)} г\n"
        f"💡 {comment_protein}\n\n"
        f"🥑 **Жиры:** {round(fat_grams)} г\n"
        f"💡 {comment_fat}\n\n"
        f"🍞 **Углеводы:** {round(carbs_grams)} г\n"
        f"💡 {comment_carbs}\n\n"
        f"📌 *Рацион: белки / жиры / углеводы*"
    )
    
    if person == "self":
        bot.send_message(
            user_id,
            answer,
            parse_mode='Markdown',
            reply_markup=friend_keyboard()
        )
        bot.send_message(
            user_id,
            "❤️ Хочешь помочь кому-то из своих?\n"
            "Это может быть друг, девушка, парень, мама, папа, брат, сестра или коллега.\n"
            "Просто нажми на кнопку ниже, и я задам те же вопросы для них.",
            parse_mode='Markdown'
        )
    else:
        bot.send_message(user_id, answer, parse_mode='Markdown')
    
    final_message = (
        f"————————————————\n\n"
        f"🔥 Подпишись на мой канал, чтобы знать больше для твоей цели:\n"
        f"👉 [ПОДПИСАТЬСЯ]({CHANNEL_LINK})\n\n"
        f"————————————————\n\n"
        f"🔄 Чтобы начать заново, напиши: /reset"
    )
    bot.send_message(user_id, final_message, parse_mode='Markdown', disable_web_page_preview=True)

# ===== КНОПКА "ДЛЯ БЛИЗКОГО" =====
@bot.message_handler(func=lambda message: message.text == "👥 Рассчитать для близкого человека")
def handle_friend_request(message):
    user_id = message.chat.id
    
    if user_id not in user_data:
        user_data[user_id] = {"self": {}, "friend": {}}
    else:
        user_data[user_id]["friend"] = {}
    
    bot.clear_step_handler(message)
    
    msg = bot.send_message(
        user_id,
        "👋 Отлично! Теперь ответь на вопросы для своего близкого человека.\n\n"
        "Сколько ему/ей лет? (напиши цифру)",
        reply_markup=ReplyKeyboardRemove()
    )
    
    bot.register_next_step_handler(msg, get_age_friend)

# ===== КОМАНДА /reset =====
@bot.message_handler(commands=['reset'])
def reset(message):
    user_id = message.chat.id
    if user_id in user_data:
        user_data[user_id] = {"self": {}, "friend": {}}
    bot.send_message(user_id, "🔄 Данные сброшены. Напиши /start для нового расчета.")

# ===== ЗАПУСК (ДЛЯ NORTHFLANK) =====
if __name__ == "__main__":
    print(">>> Запускаю polling")
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f">>> Исключение: {e}")
            traceback.print_exc()
        time.sleep(5)