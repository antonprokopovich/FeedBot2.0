#!/usr/bin/env python

import os
import sqlalchemy

from typing import Union, List, Dict, Any
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import create_engine, exists, and_

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    nickname = Column(String, unique=True)
    tg_id = Column(Integer, unique=True)
    subscriptions = relationship("Subscription", cascade="all,delete")

    def __repr__(self):
        return f"<User(id={self.id} nickname='{self.nickname}')>"


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    tg_id = Column(Integer, unique=True)

    def __repr__(self):
        return f"<Channel(id={self.id}, title='{self.title}')>"


class Subscription(Base):
    __tablename__ = 'subs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    channel_id = Column(Integer, ForeignKey('channels.id', ondelete='CASCADE'))

    channel = relationship("Channel", cascade="all,delete")
    user = relationship("User", cascade="all,delete")

    def __repr__(self):
        return f"<Subscription(id={self.id})>"


class Store:
    def __init__(self, session=None):
        self._session = session or self._create_session()

    @staticmethod
    def _create_session() -> sqlalchemy.orm.session.Session:
        """
        Создает и возвращает объект сессии, через который можно производить
        взаимодействие с БД.
        :return: sqlalchemy.orm.session.Session
        """
        db_url = os.getenv("DB_URL", None)
        engine = create_engine(db_url, echo=True)
        Session = sessionmaker(bind=engine)
        return Session()

    def session(self) -> sqlalchemy.orm.session.Session:
        if not self._session or not self._session.is_active:
            self._session = self._create_session()
        return self._session

    def save(self):
        """
        Применяет изменения, которые были произведены с объектами данных.
        """
        self.session().commit()

    def delete_user(self,
                    user_id: int = None,
                    tg_id: int = None,
                    nickname: str = None):
        """
        Удаляет пользователя, выбирая его по одному из переданных аргументов.
        :param user_id: ID пользователя в БД.
        :param tg_id: ID пользователя в Телеграме.
        :param nickname: ник пользователя в Телеграме.
        """
        stmt = None
        if user_id is not None:
            stmt = User.id == user_id
        elif tg_id is not None:
            stmt = User.tg_id == tg_id
        elif nickname is not None:
            stmt = User.nickname == nickname

        if stmt is None:
            return
        self.session().query(User).filter(stmt).delete()
        self.save()

    def delete_channel(self,
                    chan_id: int = None,
                    tg_id: int = None,
                    title: str = None):
        """
        Удаляет канал, выбирая его по одному из переданных аргументов.
        :param user_id: ID канала в БД.
        :param tg_id: ID канала в Телеграме.
        :param title: название канала в Телеграме.
        """
        stmt = None
        if chan_id is not None:
            stmt = Channel.id == chan_id
        elif tg_id is not None:
            stmt = Channel.tg_id == tg_id
        elif title is not None:
            stmt = Channel.title == title

        if stmt is None:
            return
        self.session().query(Channel).filter(stmt).delete()
        self.save()

    def delete_subscription(self, user_id: int, channel_id: int):
        """
        Удаляет подписку, выбирая ее по одному из переданных аргументов.
        :param user_id: ID пользователя в БД.
        :param channel_id: ID канала в БД.
        """
        stmt = None
        if user_id is not None:
            stmt = Subscription.user_id == user_id
        elif channel_id is not None:
            stmt = Subscription.channel_id == channel_id

        if stmt is None:
            return
        self.session().query(Subscription).filter(stmt).delete()
        self.save()

    def create_user(self, tg_id: int, nickname: str = None) -> User:
        """
        Добавляет в БД запись о пользователе с данными, переданными в аргументах.
        :param nickname: ник пользователя.
        :return: объект User c заполненными данными и его ID в БД.
        """
        s = self.session()
        new_user = User(nickname=nickname, tg_id=tg_id)
        s.add(new_user)
        s.commit()
        return new_user

    def create_channel(self, title: str, tg_id: int) -> Channel:
        """
        Добавляет в БД запись о канале с данными, переданными в аргументах.
        :param title: название канала.
        :param tg_id: ID канала в Телеграме.
        :return: объект Channel c заполненными данными и его ID в БД.
        """
        s = self.session()
        new_chan = Channel(title=title, tg_id=tg_id)
        s.add(new_chan)
        self.save()
        return new_chan

    def create_subscription(self, user_id: int, channel_id: int) -> Subscription:
        """
        Добавляет в БД запись о подписке с данными, переданными в аргументах.
        :param user_id: ID пользователя в БД.
        :param channel_id: ID канала в БД.
        :return: объект Subscription c заполненными данными и его I
        D в БД или
        None, если аргументы были некорректные.
        """
        if user_id is None or channel_id is None:
            raise Exception("Subscription creating error:"
                            "user_id or channel_id is None.")

        s = self.session()
        new_sub = Subscription(user_id=user_id, channel_id=channel_id)
        s.add(new_sub)
        self.save()
        return new_sub

    def user_exists(self,
                    nickname: str = None,
                    tg_id: int = None,
                    user_id: int = None) -> bool:
        statements = []
        if nickname is not None:
            statements.append(User.nickname == nickname)
        if tg_id is not None:
            statements.append(User.tg_id == tg_id)
        if user_id is not None:
            statements.append(User.id == user_id)

        count = self.session().query(User.id).filter(
            exists().where(and_(*statements))
        ).count()

        return count != 0

    def channel_exists(self,
                       title: str = None,
                       tg_id: int = None,
                       channel_id: int = None) -> bool:
        statements = []
        if title is not None:
            statements.append(Channel.title == title)
        if tg_id is not None:
            statements.append(Channel.tg_id == tg_id)
        if channel_id is not None:
            statements.append(Channel.id == channel_id)

        count = self.session().query(Channel.id).filter(
            exists().where(and_(*statements))
        ).count()

        return count != 0

    def subscription_exists(self, user_id: int, channel_id: int) -> bool:
        if user_id is None or channel_id is None:
            raise Exception("Subscription creating error:"
                            "user_id or channel_id is None.")
        statements = []
        if channel_id is not None:
            statements.append(Subscription.channel_id == channel_id)
        if user_id is not None:
            statements.append(Subscription.user_id == user_id)

        count = self.session().query(Subscription.id).filter(
            exists().where(and_(*statements))
        ).count()

        return count != 0

    def get_users(self,
                  user_ids: List[int] = None,
                  tg_ids: List[int] = None,
                  nicknames: List[str] = None) -> List[User]:
        """
        Возвращает список пользователей, которые соответствуют фильтрам, полученным
        из переданных аргументов. Если передано более 1 аргумента, то применяется
        операнд AND между фильтрами из этих аргументов.
        :param user_ids: ID пользователей в БД.
        :param tg_ids: ID в пользователей в Телеграме.
        :param nicknames: никнеймы пользователей в Телеграме.
        :return: список объектов User.
        """
        statements = []
        if user_ids is not None:
            statements.append(User.id.in_(user_ids))
        if tg_ids is not None:
            statements.append(User.tg_id.in_(tg_ids))
        if nicknames is not None:
            statements.append(User.nickname.in_(nicknames))

        return self.session().query(User).filter(and_(*statements)).all()

    def get_subscriptions(self,
                          sub_ids: List[int] = None,
                          channel_ids: List[int] = None,
                          user_ids: List[int] = None) -> List[Subscription]:
        """
        Возвращает список подписок, которые соответствуют фильтрам, полученным
        из переданных аргументов. Если передано более 1 аргумента, то применяется
        операнд AND между фильтрами из этих аргументов.
        :param sub_ids: ID подписок в БД.
        :param channels: каналы, по которым нужно получить подписки.
        :param users: пользователи, по которым нужно получить подписки.
        :return: список объектов Subscription.
        """
        statements = []
        if sub_ids is not None:
            statements.append(Subscription.id.in_(sub_ids))
        if channel_ids is not None:
            statements.append(Subscription.channel_id.in_(channel_ids))
        if user_ids is not None:
            statements.append(Subscription.user_id.in_(user_ids))

        return self.session().query(Subscription).filter(and_(*statements)).all()

    def get_channels(self,
                     chan_ids: List[int] = None,
                     tg_ids: List[int] = None,
                     titles: List[str] = None) -> List[Channel]:
        """
        Возвращает список каналов, которые соответствуют фильтрам, полученным
        из переданных аргументов. Если передано более 1 аргумента, то применяется
        операнд AND между фильтрами из этих аргументов.
        :param chan_ids: ID каналов в БД.
        :param titles: названия каналов в Телеграме.
        :param tg_ids: ID в каналов в Телеграме.
        :return: список объектов Channel.
        """
        statements = []
        if chan_ids is not None:
            statements.append(Channel.id.in_(chan_ids))
        if tg_ids is not None:
            statements.append(Channel.tg_id.in_(tg_ids))
        if titles is not None:
            statements.append(Channel.title.in_(titles))

        return self.session().query(Channel).filter(and_(*statements)).all()

    @staticmethod
    def _prepare_args_for_multiple_select(args: List[Any],
                                          kwargs: Dict[str, Any]
                                          ) -> (List[Any], Dict[str, Any]):
        """
        Метод конвертирует аргументы, предназначенные для получения одиночных
        значений (одного конкретного юзера или канала) для передачи их в методы
        получения множественных значений.
        Например, аргументы (123, str_arg="test") преобразуются в
        ([123], str_args=["test"]).
        :param args: неименованные аргументы.
        :param kwargs: именованные аргементы.
        :return: список и словарь сконвертированных именованных и неименованных
        аргументов.
        """
        new_args = []
        for arg in args:
            if arg is not None:
                new_args.append([arg])
            else:
                new_args.append(arg)

        new_kwargs = {}
        for arg_name, arg_value in kwargs.items():
            new_kwargs[arg_name + 's'] = [arg_value]

        return new_args, new_kwargs

    def get_user(self, *args, **kwargs) -> Union[User, None]:
        """
        Метод-обертка над методом get_users(). Подготавливает аргументы для
        get_users и вызывает его с ними, затем возвращает результат - один объект.
        :param args: аргументы, как для get_users().
        :param kwargs: именованные аргументы, как для get_users(), только
        без 's' на конце.
        :return: объект User или None (если такой объект не найден).
        """
        args, kwargs = self._prepare_args_for_multiple_select(args, kwargs)
        users = self.get_users(*args, **kwargs)
        if not len(users):
            return None
        return users[0]

    def get_channel(self, *args, **kwargs) -> Union[Channel, None]:
        """
        Метод-обертка над методом get_channels(). Подготавливает аргументы для
        get_channels и вызывает его с ними, затем возвращает результат - один объект.
        :param args: аргументы, как для get_channels().
        :param kwargs: именованные аргументы, как для get_channels(), только
        без 's' на конце.
        :return: объект Channel или None (если такой объект не найден).
        """
        args, kwargs = self._prepare_args_for_multiple_select(args, kwargs)
        channels = self.get_channels(*args, **kwargs)
        if not len(channels):
            return None
        return channels[0]
