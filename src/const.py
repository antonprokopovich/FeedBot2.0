#!/usr/bin/env python

from typing import Dict

consts = {
  "channel_name_is_empty": {
    "en": "You didn't specify channel_name.",
    "ru": "Вы не указали имя_канала.",
  },
  "channel_name_should_starts_with": {
    "en": "Channel name should start with '@' symbol. \n"
          "Please try again.",
    "ru": "Название канала должно начинаться с символа '@'.\n"
          "Попробуйте еще раз.",
  },
  "you_already_add_this_channel": {
    "en": "You have already added this channel.",
    "ru": "Вы уже добавляли данный канал.",
  },
  "channel_have_added": {
    "en": "Channel {} has been added to your feed.",
    "ru": "Канал {} добавлен в вашу рассылку.",
  },
  "no_such_channel_in_subs": {
      "en": "Channel {} is not in your subscriptions.",
      "ru": "Канала {} нет в ваших подписках"
  },
  "channel_deleted": {
      "en": "Channel {} has been deleted from your feed.",
      "ru": "Канал {} удален из вашей рассылки"
  },
  "start_msg_text": {
    "en": "Hello, {}!\n"
          "For usage reference please use /{} command.",
    "ru": "Приветствую, {}!\n"
          "Для получения справки воспользуйтесь командой /{}",
  },
  "help_msg_text": {
    "en": "/{} – get usage reference.\n"
          "/{} @channel_name – add Telegram channel.\n",
    "ru": "/{} – получить справку.\n"
          "/{} @имя_канала – добавить Телеграм-канал.\n",
  }
}


def get_constants(lang_key: str = "ru") -> Dict[str, str]:
    lang_key = lang_key.lower()
    return {
        const_name: const_value[lang_key]
        for const_name, const_value in consts.items()
    }
