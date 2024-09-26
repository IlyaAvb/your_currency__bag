from http.client import responses

import  telebot
from pyexpat.errors import messages
from telebot import types
from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
import sqlite3
import json

bot = telebot.TeleBot('7604577236:AAFJ98laDnKKSRrJF3kAupHqJClAWhUqlBA')

def crypto_mapping_check(coin):
    with open('coins.json', mode='r') as file:
        crypto_mapping = json.load(file)
        coin = coin.strip()
        if coin in crypto_mapping:
            coin = crypto_mapping[coin]
            return coin
        else:
            return coin

def create_cancel_button():
    cancel_button_keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text='ОТМЕНИТЬ', callback_data='cancel_action')
    cancel_button_keyboard.add(btn)
    return cancel_button_keyboard

def select_from_db(message):
    user_name = message.from_user.username
    status = 'active'

    response = 'Ваши сделки: \n'
    conn = sqlite3.connect('money_bag.db')
    cur = conn.cursor()

    cur.execute('SELECT coin, buy_price FROM money_bag WHERE user = ? AND status = ?', (user_name, status))
    result = cur.fetchall()

    conn.commit()
    conn.close()

    if len(result) == 0:
        response = 'У вас нет открытых сделок'
        return response
    else:
        for coin, price in result:
            response += f'{coin} - {price} USDT\n'
        return response

def calculate_the_percentages():
    pass

@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Добавить сделку 💶')
    btn2 = types.KeyboardButton('Закрыть сделку ✅')
    btn3 = types.KeyboardButton('Мой портфель 💼')
    btn4 = types.KeyboardButton('Мои сделки 📈📉')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    bot.send_message(message.chat.id,f'ВЫБЕРИ ФУНКЦИЮ',
                     reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_name = message.from_user.username
    if message.text == 'Добавить сделку 💶':
        bot.reply_to(message, 'Напишите валюту и цену, по которой вы вошли в сделку \n'
                              'Например: \n'
                              'BTC - price \n'
                              'ETH - price \n'
                              'SOL - price \n')
        bot.send_message(message.chat.id, f'Кстати, пользователь еще та ванючка\n'
                                          f'я про тебя, {message.from_user.username}')
        bot.register_next_step_handler(message, add_a_deal)

    elif message.text == 'Закрыть сделку ✅':
        bot.reply_to(message, 'Напишите монету и цену, из которой вы вошли в сделку \n'
                              'Например: \n'
                              'BTC - price \n'
                              'ETH - price \n'
                              'SOL - price \n')
        response = select_from_db(message)
        bot.send_message(message.chat.id, response)
        bot.register_next_step_handler(message, close_a_deal)

    elif message.text == 'Мой портфель 💼':
        bot.reply_to(message, 'Ваш портфель')

    elif message.text == 'Мои сделки 📈📉':
        bot.reply_to(message, 'Ваши сделки')

@bot.callback_query_handler(func=lambda call: call.data == 'cancel_action')
def cancel_action(call):
    bot.send_message(call.message.chat.id, 'Действие отменено')
    start(call.message)

def checker(message):
    if message.text in ('Добавить сделку 💶', 'Закрыть сделку ✅', 'Мой портфель 💼', 'Мои сделки 📈📉'):
        cancel_button = create_cancel_button()
        bot.send_message(message.chat.id, f'Вы находитесь в процессе «123»\n'
                                          'Нажмите «ОТМЕНИТЬ», что выбрать другую опцию', reply_markup=cancel_button)
        return False
    else:
        return True

def request_editor(message):
    request_text = message.text.strip()
    try:
        coin, price = request_text.split('-')
        coin = crypto_mapping_check(coin)
        return coin, float(price)
    except ValueError:
        return False, False


def add_a_deal(message):
    check = checker(message)
    if check == True:
        user_name = message.from_user.username
        coin, price = request_editor(message)
        sell_price = 0
        percent = 0
        status = 'active'
        if coin == False:
            bot.send_message(message.chat.id, 'Не верный формат \n'
                                              'Введите: \n'
                                              'Coin - price')
        else:
            conn = sqlite3.connect('money_bag.db')
            cur = conn.cursor()

            cur.execute('INSERT INTO money_bag (user, coin, buy_price, sell_price, percent, status) VALUES (?, ?, ?, ?, ?, ?)', (user_name, coin, price, sell_price, percent, status))

            conn.commit()
            conn.close()
            bot.send_message(message.chat.id, f'Сделка добавлена \n'
                                              f'{coin} - {price} USDT')


def close_a_deal(message):
    user_name = message.from_user.username
    coin, sell_price = request_editor(message)
    status = 'success'
    buy_price = None
    if coin == False:
        bot.send_message(message.chat.id, 'Не верный формат \n'
                                          'Введите: \n'
                                          'Coin - price')
    else:
        conn = sqlite3.connect('money_bag.db')
        cur = conn.cursor()

        cur.execute('SELECT buy_price FROM money_bag WHERE user = ? AND coin = ?',
                    (user_name, coin))

        result = cur.fetchall()
        for buy in result:
            buy_price = float(buy[0])

        conn.commit()
        conn.close()

        percent = ((sell_price - buy_price) / buy_price) * 100
        bot.send_message(message.chat.id, percent)


        conn = sqlite3.connect('money_bag.db')
        cur = conn.cursor()

        cur.execute('UPDATE money_bag SET sell_price = ?, percent = ?, status = ? WHERE user = ? AND coin = ?', (sell_price, percent, status, user_name, coin))

        conn.commit()
        conn.close()

        if percent >= 1:
            bot.send_message(message.chat.id, f'Сделка закрыта в плюс ✅\n\n'
                                              f'{coin} - (buy: {buy_price} -> sell: {sell_price}) -> {percent}% ✅')
        else:
            bot.send_message(message.chat.id, f'Сделка закрыта в минус ❌\n\n'
                                              f'{coin} - (buy: {buy_price} -> sell: {sell_price}) -> {percent}% ❌')



def my_bag(message):
    check = checker(message)
    if check == True:
        bot.send_message(message.chat.id, 'Сделка добавлена')

def my_deals(message):
    check = checker(message)
    if check == True:
        bot.send_message(message.chat.id, 'Сделка добавлена')



bot.infinity_polling()

# import sqlite3
#
# conn = sqlite3.connect('money_bag.db')
# cur = conn.cursor()
#
#
# cur.execute('CREATE TABLE IF NOT EXISTS money_bag (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, coin TEXT, buy_price REAL,sell_price REAL, percent REAL, status TEXT)')
# conn.commit()
# conn.close()
