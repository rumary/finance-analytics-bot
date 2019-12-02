import datetime
import calendar

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
days = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]


def create_callback_data(action, year, month, day):
    """
    Creates a callback data
    :param action:
    :param year:
    :param month:
    :param day:
    :return:
    """

    return ";".join([action, str(year), str(month), str(day)])


def create_calendar(year = None, month = None):
    """
    Create a built in inline keyboard with calendar
    :param year: Year to use in the calendar if you are not using the current year.
    :param month: Month to use in the calendar if you are not using the current month.
    :return: Returns an InlineKeyboardMarkup object with a calendar.
    """

    now_day = datetime.datetime.now()

    if year is None:
        year = now_day.year
    if month is None:
        month = now_day.month

    data_ignore = create_callback_data("IGNORE", year, month, "")
    data_months = create_callback_data("MONTHS", year, month, "")

    keyboard = InlineKeyboardMarkup(row_width=7)

    keyboard.add(InlineKeyboardButton(months[month - 1] + " " + str(year), callback_data=data_months))

    keyboard.add(*[InlineKeyboardButton(day, callback_data=data_ignore) for day in days])

    for week in calendar.monthcalendar(year, month):
        row = list()
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data=data_ignore))
            elif "{}.{}.{}".format(now_day, now_day.month, now_day.year) == "{}.{}.{}".format(day, month, year):
                row.append(
                    InlineKeyboardButton("{}".format(day), callback_data=create_callback_data("DAY", year, month, day)))
            else:
                row.append(InlineKeyboardButton(str(day), callback_data=create_callback_data("DAY", year, month, day)))
        keyboard.add(*row)

    keyboard.add(InlineKeyboardButton("<", callback_data=create_callback_data("PREVIOUS-MONTH", year, month, "")),
                 InlineKeyboardButton("Cancel", callback_data=create_callback_data("CANCEL", year, month, "")),
                 InlineKeyboardButton(">", callback_data=create_callback_data("NEXT-MONTH", year, month, "")),
                 InlineKeyboardButton("Today", callback_data=create_callback_data("TODAY", year, month, "")))

    return keyboard


def create_months_calendar(year = None):
    """
    Creates a calendar with month selection
    :param year:
    :return:
    """

    if year is None:
        year = datetime.datetime.now().year

    keyboard = InlineKeyboardMarkup()

    for i, month in enumerate(zip(months[0::2], months[1::2])):
        keyboard.add(InlineKeyboardButton(month[0], callback_data=create_callback_data("MONTH", year, i + 1, "")),
                     InlineKeyboardButton(month[1], callback_data=create_callback_data("MONTH", year, (i + 1) * 2, "")))

    return keyboard


def calendar_query_handler(bot, call):
    """
    The method creates a new calendar if the forward or backward button is pressed
    This method should be called inside CallbackQueryHandler.
    :param bot: The object of the bot CallbackQueryHandler
    :param call: CallbackQueryHandler data
    :return: Returns a tuple
    """

    action, year, month, day = call.data.split(";")
    current = datetime.datetime(int(year), int(month), 1)
    if action == "IGNORE":
        bot.answer_callback_query(callback_query_id=call.id)
        return False, None
    elif action == "DAY":
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        return "DAY", datetime.datetime(int(year), int(month), int(day))
    elif action == "PREVIOUS-MONTH":
        preview_month = current - datetime.timedelta(days=1)
        bot.edit_message_text(text=call.message.text,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=create_calendar(int(preview_month.year), int(preview_month.month)))
        return None, None
    elif action == "NEXT-MONTH":
        next_month = current + datetime.timedelta(days=31)
        bot.edit_message_text(text=call.message.text,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=create_calendar(int(next_month.year), int(next_month.month)))
        return None, None
    elif action == "MONTHS":
        bot.edit_message_text(text=call.message.text,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=create_months_calendar(current.year))
        return "MONTH", None
    elif action == "MONTH":
        bot.edit_message_text(text=call.message.text,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=create_calendar(int(year), int(month)))
        return None, None
    elif action == "CANCEL":
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        return "CANCEL", None
    elif action == "TODAY":
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        return "TODAY", None
    else:
        bot.answer_callback_query(callback_query_id=call.id, text="ERROR!")
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        return None, None

