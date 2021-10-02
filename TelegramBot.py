import telebot
import json
import config
from datetime import datetime

data_file = config.data
bot = telebot.TeleBot(config.TOKEN)
print(datetime.now())


def get_data(data_file):
    with open(data_file, 'r') as f:
        raw_data = f.read()
        if raw_data:
            return json.loads(raw_data)
        return {}


def put(data_file, data):
    with open(data_file, 'w') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))


@bot.message_handler(commands=['start'])
def start(message):
    data = get_data(data_file)
    chat_id = str(message.chat.id)
    if chat_id in data:
        bot.send_message(message.chat.id,
                         """
        Привет! Меня зовут КочкоБот.
    Я умею сохранять прогресс твоих КочкоЦелей.
    Ты уже зарегистрирован.
    Если есть вопросы по функциям, напиши /help
        """)
    else:
        data[chat_id] = {"users": {}}
        put(data_file, data)
        bot.send_message(message.chat.id,
                         """
        Привет! Меня зовут КочкоБот.
        Я умею сохранять прогресс твоих КочкоЦелей.
        Зарегистрируйся, чтобы начать /register
        Если есть вопросы по функциям, напиши /help
        """)


@bot.message_handler(commands=['register'])
def register(message):
    data = get_data(data_file)
    chat_id = str(message.chat.id)
    if chat_id in data:
        if str(message.from_user.id) in data[chat_id]["users"]:
            bot.send_message(
                message.chat.id, "Ты уже кочка, {0.first_name}".format(message.from_user))
        else:
            new_user = {
                "username": message.from_user.username,
                "ratings": {
                    "workouts_done": 0,
                    "challenges_done": 0,
                    "challanges_failed": 0
                },
                "exercises": {
                    "quantity": 0
                },
                "workouts": {
                    "quantity": 0
                }
            }
            data[chat_id]["users"][str(message.from_user.id)] = new_user
            with open(data_file, 'w') as f:
                f.write(json.dumps(data, ensure_ascii=False, indent=4))
            bot.send_message(
                message.chat.id, "Теперь ты кочка, {0.first_name}".format(message.from_user))


@bot.message_handler(commands=['create'])
def create(message):
    data = get_data(data_file)
    chat_id = str(message.chat.id)
    if chat_id in data:
        if str(message.from_user.id) in data[chat_id]["users"]:
            message_text = message.text
            mess = message_text.split(' ')
            if len(mess) != 2:
                msg = bot.send_message(
                    message.chat.id, "Какую цель хочешь создать? Упражнение (напиши 1) или тренировки (напиши 2)")
                bot.register_next_step_handler(
                    msg, choose_goal)

            elif mess[1].lower() in config.exercise:
                msg = bot.send_message(
                    message.chat.id, "Напиши название упражнения")
                bot.register_next_step_handler(msg, create_ex_name)

            elif mess[1].lower() in config.workout:
                msg = bot.send_message(
                    message.chat.id, 'Напиши свою цель и дату окончания в формате "Цель дд.мм.гггг"')
                bot.register_next_step_handler(msg, create_w_goal_n_date)
            else:
                bot.send_message(
                    message.chat.id, 'Такого варианта нет...')
        else:
            bot.send_message(
                message.chat.id, "Сначала зарегистрируйся /register")


def choose_goal(message):
    if message.text.lower() in ["1", "упражнение", "упр", "ex"]:
        msg = bot.send_message(
            message.chat.id, "Напиши название упражнения")
        bot.register_next_step_handler(msg, create_ex_name)

    elif message.text.lower() in ["2", "тренировка", "wo", "workout"]:
        msg = bot.send_message(
            message.chat.id, 'Напиши свою цель и дату окончания в формате "Цель дд.мм.гггг"')
        bot.register_next_step_handler(msg, create_w_goal_n_date)
    elif message.text in "3":
        pass
    else:
        msg = bot.send_message(
            message.chat.id, "Какую цель хочешь создать? Упражнение (напиши 1) или тренировки (напиши 2). Чтобы выйти введи 3")
        bot.register_next_step_handler(msg, choose_goal)


def create_ex_name(message):
    data = get_data(data_file)
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)

    exercise_data = {
        "name": message.text,
        "goal": 0,
        "start_date": None,
        "finish_date": None,
        "now": 0,
        "filling": False,
        "in_progress": True
    }
    data[chat_id]["users"][user_id]["exercises"]["quantity"] += 1
    quantity = data[chat_id]["users"][user_id]["exercises"]["quantity"]
    data[chat_id]["users"][user_id]["exercises"]["ex_" +
                                                 str(quantity)] = exercise_data
    put(data_file, data)
    msg = bot.send_message(
        message.chat.id, 'Напиши свою цель - количество повторений и время окончания в формате "dd.mm.yyyy" через пробел')
    bot.register_next_step_handler(msg, create_ex_goal_n_date)


def create_ex_goal_n_date(message):
    data = get_data(data_file)
    chat_id = str(message.chat.id)
    quantity = data[chat_id]["users"][str(
        message.from_user.id)]["exercises"]["quantity"]
    message_text = message.text
    mess = message_text.split(' ')

    data[chat_id]["users"][str(
        message.from_user.id)]["exercises"]["ex_" + str(quantity)]["goal"] = mess[0]
    data[chat_id]["users"][str(
        message.from_user.id)]["exercises"]["ex_" + str(quantity)]["finish_date"] = mess[1]
    put(data_file, data)
    exercise = data[chat_id]["users"][str(
        message.from_user.id)]["exercises"]["ex_" + str(quantity)]
    bot.send_message(
        chat_id, 'Упражнение "{0[name]}" с целью {0[goal]} повторений до {0[finish_date]} установлено'.format(exercise))
    bot.send_message(
        chat_id, "{0[0]} и {0[1]}".format(mess))


def create_w_goal_n_date(message):
    data = get_data(data_file)
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    message_text = message.text
    mess = message_text.split(' ')

    workout_data = {
        "goal": mess[0],
        "start_date": message.date,
        "finish_date": mess[1],
        "now": 0,
        "filling": False,
        "in_progress": True
    }
    data[chat_id]["users"][user_id]["workouts"]["quantity"] += 1
    quantity = data[chat_id]["users"][user_id]["workouts"]["quantity"]
    data[chat_id]["users"][user_id]["workouts"]["w_" +
                                                str(quantity)] = workout_data
    put(data_file, data)

    workout = data[chat_id]["users"][str(
        message.from_user.id)]["workouts"]["w_" + str(quantity)]
    bot.send_message(
        chat_id, 'Цель {0[goal]} тренировок до {0[finish_date]} установлена'.format(workout))
    bot.send_message(
        chat_id, "{0[0]} и {0[1]}".format(mess))


@bot.message_handler(commands=['add'])
def add(message):
    data = get_data(data_file)
    chat_id = str(message.chat.id)
    if chat_id in data:
        if str(message.from_user.id) in data[chat_id]["users"]:
            user_id = str(message.from_user.id)
            text_message = "Выбери упражнение или тренировку, которую собираешься изменять:\n\n" + "Упражнения:\n"
            text_exercises = str()
            text_workouts = str()
            info = data[chat_id]["users"][user_id]
            num = 1
            for n in info["exercises"]:
                if n != "quantity":
                    text_exercises += str("/" + num + " - " +
                                          info["exercises"][n]["name"] + "\n")
                    num += 1
            for n in info["workouts"]:
                if n != "quantity":
                    text_workouts += str("/" + num + " - " +
                                         info["workouts"][n]["goal"] + " тренировок" + "\n")
                    num += 1
            text_message = text_message + text_exercises + "\nТренировки:\n" + \
                text_workouts + "\nВыбери упражнение\тренировку или нажми /0, чтобы отменить"
            msg = bot.send_message(message.chat.id, text_message)
            bot.register_next_step_handler(msg, choose_type)


def choose_type(message):
    data = get_data(data_file)
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    info = data[chat_id]["users"][user_id]
    ex_q = info["exercises"]["quantity"]
    w_q = info["workouts"]["quantity"]
    if message.text[0] in '/' and message.text[1:].isdigit():
        if int(message.text[1:]) <= ex_q:
            ex = info["exercises"]["ex_" + message.text[1:]]
            data[chat_id]["users"][user_id]["exercises"]["ex_" +
                                                         message.text[1:]]["filling"] = True
            text = str(
                "Упражнение: {0[name]}\n" + "Цель: {0[goal]}\n" + "Сделано: {0[now]}").format(ex)
            msg = bot.send_message(chat_id, text)
            bot.register_next_step_handler(msg, add_reps_ex)
            put(data_file, data)

        elif int(message.text[1:]) <= (ex_q + w_q):
            w = info["workouts"]["ex_" + message.text[1:]]
            data[chat_id]["users"][user_id]["workouts"]["w_" +
                                                        message.text[1:]]["filling"] = True
            text = str(
                "Упражнение: {0[name]}\n" + "Цель: {0[goal]}\n" + "Сделано: {0[now]}").format(w)
            msg = bot.send_message(chat_id, text)
            bot.register_next_step_handler(msg, add_reps_w)
            put(data_file, data)
        else:
            pass


def filling_search():
    reps = message.text


def add_reps_ex(message):
    if message.text.is_digit():
        data = get_data(data_file)
        chat_id = str(message.chat.id)
        user_id = str(message.from_user.id)
        filling_search()


def add_reps_w(message):
    data = get_data(data_file)
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    filling_search()


@bot.message_handler(commands=['help'])
def help(message):
    data = get_data(data_file)
    chat_id = str(message.chat.id)
    bot.send_message(message.chat.id, "Ghbdtn")


# RUN
bot.polling(none_stop=True)
