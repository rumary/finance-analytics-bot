# -*- coding: utf-8 -*-
import re
from telebot import types
from datetime import datetime
#from sqlite import SQLighter
from postres import Postgres
from nltk.tag.perceptron import PerceptronTagger


def split_message(message):
    expression = r'([0-9.]+)\s*(.*)'
    price, category = re.findall(expression, message)[0]
    category_3 = 'крупноe' if int(price) > 5000 else 'текущее'

    return int(price), category, category_3


def define_category_2(category, categories):
    category_2 = None
    for key, value in categories.iteritems():
        if category in value:
            category_2 = key
            break

    return category_2


def insert(date, price, category, category_2, category_3, database_name):
    db_worker = Postgres(database_name)
    db_worker.insert(date, price, category, category_2, category_3)
    db_worker.close()


def generate_markup(categories):
    markup = types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True, resize_keyboard=True)
    for category in categories:
        markup.add(category)

    return markup


def select(database_name, start_date):
    db_worker = Postgres(database_name)
    data = db_worker.select_weekly_spends(start_date)
    db_worker.close()
    return data



