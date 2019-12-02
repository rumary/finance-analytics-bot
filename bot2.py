# -*- coding: utf-8 -*-
import config
import telebot
import pandas as pd
from datetime import datetime
import utils
from telebot import types
import telebot_calendar
import json
import logging

bot = telebot.TeleBot(config.token)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

spending = {}
global categories
with open('categories', 'r') as configfile:
    categories = json.load(configfile)

global date
date = datetime.today().strftime('%Y-%m-%d')


@bot.message_handler(commands=["start"])
def welcome(message):
    bot.send_message(message.chat.id, 'Привет! Я бот, анализирующий твои траты и доходы. '
                                      'Записывай сюда все свои траты в течении недели, а если забудешь - я буду тебе '
                                      'напоминать. По умолчанию дата траты - сегодня, если хочешь сменить дату '
                                      'выбери команду /change_date '
                                      'Записывай траты в формате - 555 азбука вкуса. С помощью команд  '
                                      '/add и /create ты можешь добавлять статью трат в существующую категорию и '
                                      'создавать новые категории, например, "цветы для Маши". Удачи и экономии!')


@bot.message_handler(commands=['change_date'])
def define_date(message):
    now = datetime.now()
    bot.send_message(message.chat.id, "Выбери дату",
                     reply_markup=telebot_calendar.create_calendar(now.year, now.month))


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """
    Обработка inline callback запросов
    :param call:
    :return:
    """
    data = call.data.split(";")
    print data
    if len(data) > 1:
        type_selected, date_new = telebot_calendar.calendar_query_handler(bot, call)
        print type_selected, date_new
        if type_selected == "DAY":
            bot.send_message(chat_id=call.from_user.id,
                             text="Дата покупок выбрана - {}".format(date_new.strftime('%Y-%m-%d')),
                             reply_markup=types.ReplyKeyboardRemove())
            global date
            date = date_new.strftime('%Y-%m-%d')

        elif type_selected == "CANCEL":
            bot.send_message(chat_id=call.from_user.id,
                             text="Cancellation",
                             reply_markup=types.ReplyKeyboardRemove())
            print("Cancellation")

        elif type_selected == "TODAY":
            bot.send_message(chat_id=call.from_user.id,
                             text="Дата покупок выбрана - {}".format(datetime.today().strftime('%Y-%m-%d')),
                             reply_markup=types.ReplyKeyboardRemove())
            date = datetime.today().strftime('%Y-%m-%d')


@bot.message_handler(regexp=r'([0-9.]+)\s*(.*)')
def split(message):
    global category_2
    global categories
    global category
    with open('categories', 'r') as configfile:
        categories = json.load(configfile)
    price, category, category_3 = utils.split_message(message.text)
    spending['date'] = date
    spending['price'] = price
    spending['category'] = category
    spending['category_3'] = category_3

    category_2 = utils.define_category_2(category, categories)
    if not category_2:
        bot.send_message(message.chat.id, 'Такой траты еще не было, создай новую категорию (/create) '
                                          'или добавь в существующую (/add)!')
        bot.register_next_step_handler_by_chat_id(message, define_next_step)
    else:
        spending['category_2'] = category_2
        utils.insert(spending['date'], spending['price'], spending['category'], spending['category_2'],
                     spending['category_3'], config.database_name)
        # print pd.DataFrame(utils.select(config.database_name))


@bot.message_handler(commands=['add', 'create'])
def define_next_step(message):
    if message.text == '/add' or message.text == 'add':
        bot.send_message(message.chat.id, 'Выбери категорию траты')
        bot.register_next_step_handler(message, select_category)
    elif message.text == '/create' or message.text == 'create':
        bot.send_message(message.chat.id, "Окей, напиши название новой категории. Cуществующие категории: {}"
                         .format(', '.join(list(map(lambda x: x.encode('utf-8'), categories.keys())))))
        # bot.send_message(message.chat.id, ', '.join(categories.keys()))
        bot.register_next_step_handler(message, create_category)
    else:
        bot.reply_to(message, 'Выбери команду еще раз!')


@bot.message_handler(commands=['add'])
def select_category(message):
    markup = utils.generate_markup(categories)
    bot.send_message(message.chat.id, 'Категории', reply_markup=markup)
    bot.register_next_step_handler(message, add_to_category)


def add_to_category(message):
    keyboard_hider = types.ReplyKeyboardRemove()
    if message.text != 'create' or message.text != '/create' or message.text != '/exit':
        category_2 = message.text
        categories[category_2].append(category)
        with open('categories', 'w') as configfile:
            json.dump(categories, configfile, indent=2)
        bot.send_message(message.chat.id, 'Добавлено!', reply_markup=keyboard_hider)
        spending['category_2'] = category_2
        utils.insert(spending['date'], spending['price'], spending['category'], spending['category_2'],
                     spending['category_3'], config.database_name)
    elif message.text == 'create' or message.text == '/create':
        bot.register_next_step_handler(message, create_category)
    else:
        bot.send_message(message.chat.id, 'Попробуй еще раз!', reply_markup=keyboard_hider)
        bot.register_next_step_handler(message, select_category)


def create_category(message):
    if message.text:
        category_2 = message.text
        categories[category_2] = [category]
        with open('categories', 'w') as configfile:
            json.dump(categories, configfile, indent=2)
        bot.send_message(message.chat.id, 'Создана новая категория!')
        spending['category_2'] = category_2
        utils.insert(spending['date'], spending['price'], spending['category'], spending['category_2'],
                     spending['category_3'], config.database_name)


@bot.message_handler(commands=['analytics'])
def select_data(message):
    data = utils.select(config.database_name, datetime.today().strftime('%Y-%m-%d'))
    df = pd.DataFrame(data)[0].sum()
    bot.send_message(message.chat.id, 'Траты за неделю : {} руб.'.format(int(df)))
    print df


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
