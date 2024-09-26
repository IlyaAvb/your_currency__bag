import telebot
from pyexpat.errors import messages
from telebot import types
from telebot.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup



bot = telebot.TeleBot('7604577236:AAFJ98laDnKKSRrJF3kAupHqJClAWhUqlBA')


def create_cancel_btn(message):
    keyboard = types.InlineKeyboardMarkup()
    cancel_button = types.InlineKeyboardButton(text='Отменить действие', callback_data='cancel_action')
    keyboard.add(cancel_button)
    return keyboard


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn3 = types.KeyboardButton('Добавить сделку 💶')
    btn4 = types.KeyboardButton('Закрыть сделку ✅')

    markup.row(btn3, btn4)
    bot.send_message(message.chat.id, f'Привет {message.from_user.username or message.from_user.first_name} \n'
                                      f'Я твой портфель и буду показывать твои успешные и не очень сделки',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id

    if message.text == 'Добавить сделку 💶':
        bot.reply_to(message, 'Напишите валюту и цену, по которой вы вошли в сделку \n'
                              'Например: \n'
                              'BTC - price \n'
                              'ETH - price \n'
                              'SOL - price \n')
        bot.register_next_step_handler(message, add_a_deal)

    elif message.text == 'Закрыть сделку ✅':
        bot.reply_to(message, 'Напишите валюту из которой вы вышли \n'
                              'Например: \n'
                              'BTC \n'
                              'ETH\n'
                              'SOL\n')
        bot.register_next_step_handler(message, close_a_deal)

@bot.callback_query_handler(func=lambda call: call.data == 'cancel_action')
def cancel_action(call):
    bot.send_message(call.message.chat.id, 'Действие отменено. Выберите следующее действие:')
    start(call.message)


def add_a_deal(message):
    # Проверка на случай, если пользователь снова попытается начать новый процесс
    cancel_button = create_cancel_btn(message)
    if message.text == 'Закрыть сделку ✅':
        bot.send_message(message.chat.id, 'Сначала завершите добавление сделки.', reply_markup=cancel_button)
        return

    # Логика для обработки входа в сделку
    bot.send_message(message.chat.id, 'Сделка добавлена')


def close_a_deal(message):
    user_id = message.from_user.id

    # Проверка на случай, если пользователь снова попытается начать новый процесс
    if message.text == 'Добавить сделку 💶':
        bot.send_message(message.chat.id, 'Сначала завершите закрытие сделки.')
        return
    else:
        bot.send_message(message.chat.id, 'ADD')


    # Логика для обработки выхода из сделки
    bot.send_message(message.chat.id, 'Сделка закрыта')


bot.infinity_polling()