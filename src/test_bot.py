#!/usr/bin/env python

import os
import unittest

from unittest.mock import Mock, MagicMock
from bot import FeedBot
from dal import User, Channel, Subscription
from const import get_constants

consts = get_constants(os.getenv("BOT_LANG", "ru").lower())


class TestFeedBotAddCommand(unittest.TestCase):
    def setUp(self) -> None:
        # Подготавливаем объект хранилища (делаем стаб-методы). Подробнее см.
        # здесь: https://bit.ly/2ZYegxl

        self.user_stub = Mock(spec=User)
        self.user_stub.id = 123
        self.user_stub.nickname = "stub_user"

        self.channel_stub = Mock(spec=Channel)
        self.channel_stub.id = 456
        self.channel_stub.title = "stub_channel"

        store_mock = Mock()
        store_mock.get_user = Mock(return_value=self.user_stub)
        store_mock.get_channel = Mock(return_value=None)
        store_mock.create_channel = Mock(return_value=self.channel_stub)
        store_mock.create_subscription = MagicMock(name="create_subscription")

        self.bot = FeedBot(store=store_mock)

    def test_none_args(self):
        # Проверяем, что вернется текст сообщения о "пустом" названии канала.
        self.assertEqual(
            consts["channel_name_is_empty"],
            self.bot._handle_add_channel(self.user_stub.id, "")
        )

    def test_incorrect_channel_name(self):
        # Проверяем, что вернется сообщение о некорректном формате названия канала.
        self.assertEqual(
            consts["channel_name_should_starts_with"],
            self.bot._handle_add_channel(self.user_stub.id, "not_a_channel")
        )

    def test_already_added_channel(self):
        self.bot.store.subscription_exists = Mock(return_value=True)
        # Проверяем, что вернется сообщение об уже существующей подписке.
        self.assertEqual(
            consts["you_already_add_this_channel"],
            self.bot._handle_add_channel(self.user_stub.id, "@existing_channel")
        )

    def test_first_adding_channel(self):
        self.bot.store.subscription_exists = Mock(return_value=False)
        # Проверяем, что вернется сообщение о созданной подписке.
        self.assertEqual(
            consts["channel_have_added"].format("@test_channel"),
            self.bot._handle_add_channel(self.user_stub.id, "@test_channel")
        )
        # Проверяем, что у хранилища вызывался метод создания подписки с
        # переданными аргументами.
        self.bot.store.create_subscription.assert_called_once_with(
            self.user_stub.id, self.channel_stub.id
        )


class TestFeedBotAddCommandOld(unittest.TestCase):
    def setUp(self) -> None:
        # Подготавливаем объект хранилища (делаем стаб-методы). Подробнее см.
        # здесь: https://bit.ly/2ZYegxl

        self.user_stub = Mock(spec=User)
        self.user_stub.id = 123
        self.user_stub.nickname = "stub_user"

        self.channel_stub = Mock(spec=Channel)
        self.channel_stub.id = 456
        self.channel_stub.title = "stub_channel"

        store_mock = Mock()
        store_mock.get_user = Mock(return_value=self.user_stub)
        store_mock.get_channel = Mock(return_value=None)
        store_mock.create_channel = Mock(return_value=self.channel_stub)
        store_mock.create_subscription = MagicMock(name="create_subscription")

        self.update_stub = Mock()
        self.update_stub.message = Mock()
        self.update_stub.message.chat = Mock()
        self.update_stub.message.reply_text = MagicMock(name="reply_text")
        self.update_stub.message.chat.id = 789

        self.bot = FeedBot(store=store_mock)

    def test_none_args(self):
        # Проверяем, что вернется текст сообщения о "пустом" названии канала.
        self.bot.add_channel_old(None, self.update_stub, [])
        self.update_stub.message.reply_text.assert_called_once_with(
            consts["channel_name_is_empty"]
        )

    def test_incorrect_channel_name(self):
        # Проверяем, что вернется сообщение о некорректном формате названия канала.
        self.bot.add_channel_old(None, self.update_stub, "not_a_channel")
        self.update_stub.message.reply_text.assert_called_once_with(
            consts["channel_name_should_starts_with"]
        )

    def test_already_added_channel(self):
        self.bot.store.subscription_exists = Mock(return_value=True)
        # Проверяем, что вернется сообщение об уже существующей подписке.
        self.bot.add_channel_old(None, self.update_stub, "@existing_channel")
        self.update_stub.message.reply_text.assert_called_once_with(
            consts["you_already_add_this_channel"]
        )

    def test_first_adding_channel(self):
        self.bot.store.subscription_exists = Mock(return_value=False)
        # Проверяем, что вернется сообщение о созданной подписке.
        self.bot.add_channel_old(None, self.update_stub, "@test_channel")
        self.update_stub.message.reply_text.assert_called_once_with(
            consts["channel_have_added"].format("@test_channel")
        )
        # Проверяем, что у хранилища вызывался метод создания подписки с
        # переданными аргументами.
        self.bot.store.create_subscription.assert_called_once_with(
            self.user_stub.id, self.channel_stub.id
        )
