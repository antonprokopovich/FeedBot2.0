# -*- coding: utf-8 -*-

import traceback
import os
#from telethon import TelegramClient, events, sync

from dal import User, Channel, Subscription, Store
from const import get_constants
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, Bot

START_CMD = "start"
HELP_CMD = "help"
ADD_CMD = "add"
DEL_CMD = "del"

consts = get_constants(os.getenv("BOT_LANG", "ru").lower())


def quiet_exec(f):
    def wrapper(*args, **kw):
        try:
            return f(*args, **kw)
        except BaseException as e:
            e = "Error in {}(): {}\n{}".format(
                f.__name__, str(e), traceback.format_exc()
            )
            print(e)

    return wrapper


class FeedBot:

    def __init__(self, store):
        self.store = store

    def start(self, bot, update):
        """
        Хэндлер команды /start, которая отправляется от пользователя боту
        автоматически при отправке.
        """
        # При начале работы с ботом автоматически вызывается команда /start
        # и пользователю присвается user_id, под которым он заносится в БД.
        user_id = update.message.chat.id

        # Имя или юзернейм пользователя для приветствия.
        fname = update.message.from_user.first_name
        username = update.message.from_user.username
        if not fname:
            fname = username

        channel_name = "@{}{}".format(user_id, fname)

        msg = consts["start_msg_text"].format(fname, channel_name, HELP_CMD)

        update.message.reply_text(msg)
        # При старте работы с ботом заносим id юзера и название канала в БД.
        # Если пользователь повторно воспользовался командой /start,
        # и его данные уже есть в таблице - не меняем их.
        self.store.create_user(fname)

    def help(self, bot, update):
        """
        Хэндлер команды /help, которая дает справку о командах бота
        """
        msg = consts["help_msg_text"].format(HELP_CMD, ADD_CMD, DEL_CMD)
        update.message.reply_text(msg)

    def delete_channel(self, bot, update, args):
        """
        Хэндлер команды /leave_channel и ее аргумента, которая удаляет из
        списка рассылок канал указанный в качестве аргумента.
        """
        user_id = update.message.chat.id
        channel_name = ''.join(args) if args is not None else ''
        update.message.reply_text(
            self._handle_delete_channel(user_id, channel_name)
        )

    def _handle_delete_channel(self, user_id: int, channel_name: str) -> str:
        if not channel_name:
            return consts["channel_name_is_empty"]

        if not channel_name.startswith('@'):
            return consts["channel_name_should_starts_with"]

        user = self.store.get_user(tg_id=[user_id])
        channel = self.store.get_channel(title=[channel_name])

        if not self.store.subscription_exists(user.id, channel.id):
            return consts["no_such_channel_in_subs"]

        # Удаляем запись о подписке юзера на канал.
        self.store.delete_subscription(user.id, channel.id)

        return consts["channel_deleted"].format(channel_name)

    def add_channel(self, bot, update, args):
        """
        Хэндлер команды /add_channel и ее аргумента, которая добавляет в
        список рассылок телеграм-канал указанный в качестве аргумента.
        """
        user_id = update.message.chat.id
        channel_name = ''.join(args) if args is not None else ''
        update.message.reply_text(
            self._handle_add_channel(user_id, channel_name)
        )

    def _handle_add_channel(self, user_id: int, channel_name: str) -> str:
        if not channel_name:
            return consts["channel_name_is_empty"]

        if not channel_name.startswith('@'):
            return consts["channel_name_should_starts_with"]

        user = self.store.get_user(tg_id=[user_id])
        channel = self.store.get_channel(title=[channel_name])
        # Если этого канала еще нет в БД - добавляем.
        if channel is None:
            channel = self.store.create_channel(channel_name)

        if self.store.subscription_exists(user.id, channel.id):
            return consts["you_already_add_this_channel"]

        # Создаем запись о подписке юзера на канал.
        self.store.create_subscription(user.id, channel.id)

        return consts["channel_have_added"].format(channel_name)

    def add_channel_old(self, bot, update, args):
        """
        Хэндлер команды /add_channel и ее аргумента, которая добавляет в
        список рассылок телеграм-канал указанный в качестве аргумента.
        """
        user_id = update.message.chat.id
        channel_name = ''.join(args) if args is not None else ''

        if not channel_name:
            update.message.reply_text(consts["channel_name_is_empty"])
            return

        if not channel_name.startswith('@'):
            update.message.reply_text(consts["channel_name_should_starts_with"])
            return

        user = self.store.get_user(tg_id=[user_id])
        channel = self.store.get_channel(title=[channel_name])
        # Если этого канала еще нет в БД - добавляем.
        if channel is None:
            channel = self.store.create_channel(channel_name)

        if self.store.subscription_exists(user.id, channel.id):
            update.message.reply_text(consts["you_already_add_this_channel"])
            return

        # Создаем запись о подписке юзера на канал.
        self.store.create_subscription(user.id, channel.id)

        update.message.reply_text(
            consts["channel_have_added"].format(channel_name)
        )


if __name__ == "__main__":
    token = os.getenv('BOT_TOKEN', None)
    feedbot = FeedBot(store=Store())
    updater = Updater(bot=Bot(token))

    updater.dispatcher.add_handler(CommandHandler(START_CMD, feedbot.start))
    updater.dispatcher.add_handler(CommandHandler(HELP_CMD, feedbot.help))
    updater.dispatcher.add_handler(CommandHandler(ADD_CMD, feedbot.add_channel, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler(DEL_CMD, feedbot.delete_channel, pass_args=True))

    updater.start_polling()
    updater.idle()
