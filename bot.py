import telebot
import random
from telebot import types

bot = telebot.TeleBot('6404942460:AAHNVBY1AiSNzjDuRMwS3fo7Jmao8I7zTKg')
users = {}
dictionary = {}

def open_file():
    global dictionary
    with open('ENRUS1.TXT', 'r', encoding='cp1251') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 2):
            english_word = lines[i].strip()
            russian_translation = lines[i + 1].strip()
            if len(russian_translation) <= 40:  # Проверяем, что длина перевода не превышает 64 символа
                dictionary[english_word] = russian_translation
                x = dictionary[english_word]
    return dictionary



@bot.message_handler(commands=['start'])
def main(message):
    markup = types.InlineKeyboardMarkup()
    btn_webapp = types.InlineKeyboardButton('Открыть веб-приложение', url='https://www.gubkin.ru/faculty/humanities/chairs_and_departments/foreign_language/')
    markup.add(btn_webapp)

    bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}, начнем учить англиский с ботом от РГУНГ? А чтобы знать английский ещё лучше жми на кнопку👇' , reply_markup=markup)



def inlineKeyboard(message, english_word, correct_translation):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Показать ответ', callback_data = correct_translation)
    markup.add(button)
    bot.send_message(message.chat.id, f'Переведите слово: {english_word}', reply_markup = markup)



@bot.message_handler(func=lambda message: message.text.lower() == 'да')
def yes(message):
    user_id = message.from_user.id
    users.setdefault(user_id, {"attempts":3,"general":0,"correct":0,"wrong":0})


    attempts = users[user_id]["attempts"]
    general = users[user_id]["general"]


    user = users[user_id]
    user["general"] += 1


    english_word = random.choice(list(dictionary.keys()))
    correct_translation = dictionary[english_word]
    inlineKeyboard(message, english_word, correct_translation)
    bot.register_next_step_handler(message, on_answer, correct_translation, english_word, attempts, user)


@bot.message_handler(func=lambda message: message.text.lower() == 'нет')
def no(message):
    bot.send_message(message.chat.id, f'Жаль, возвращайся скорее!')


def on_answer(message, correct_translation, english_word, attempts, user):
    user_translation = message.text.lower()
    user_words = user_translation.split()
    correct_words = set(correct_translation.lower().split())
    is_correct = any(word in correct_words for word in user_words)



    english_word1 = english_word.split()
    if is_correct and len(user_words) == len(english_word1):
        bot.send_message(message.chat.id, f'Верно, продолжим?')
        user["correct"] += 1
    else:
        user["wrong"] += 1
        if attempts - 1 != 0:
            bot.send_message(message.chat.id, f'Ответ неверный, осталось {attempts - 1} попытки')
            attempts -= 1
            bot.register_next_step_handler(message, lambda message: on_answer(message, correct_translation, english_word, attempts, user))
        elif attempts - 1 == 0:
            bot.send_message(message.chat.id, f'Неверно, правильный перевод: {correct_translation}. Попробуем еще?')

@bot.callback_query_handler(func = lambda call: True)
def callback_massage(call):
    bot.send_message(call.message.chat.id, f'Как скажешь, перевод: {call.data}. Попробуем еще?')
    bot.clear_step_handler_by_chat_id(call.message.chat.id)

@bot.message_handler(commands=['statistics'])
def statistics(message):
    user_id = message.from_user.id
    user = users.get(user_id, {"attempts":3,"general":0,"correct":0,"wrong":0})
    general = user["general"]

    if user["correct"] == 0 and general >= 10:
        bot.send_message(message.chat.id, f'Твой результат {user["correct"]}/{general}. Даввай учиться, попробуем ещё?')
    if general >= 10:
      if general == user["correct"]:
          bot.send_message(message.chat.id, f'Твой результат {user["correct"]}/{general}. Уровень: ПРОФИ, продолжим?')
      if user["correct"] != 0 and general / user["correct"] < 2 and general != user["correct"]:
          bot.send_message(message.chat.id,f'Твой результат {user["correct"]}/{general}. Не унывай, всё плучится, попробуем ещё?')
      if user["correct"] != 0 and general / user["correct"] >= 2:
        bot.send_message(message.chat.id,  f'Твой результат {user["correct"]}/{general}. Есть куда расти, попробуем ещё?')
    else:
        bot.send_message(message.chat.id, f'Статистика будет доступна после 10 заданных слов. Сейчас заданно {general}. Продолжим?')




open_file()
bot.polling(non_stop = True)