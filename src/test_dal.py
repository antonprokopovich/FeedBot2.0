#!/usr/bin/env python

import os
import pytest
import factory
import dal

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dal import Store

engine = create_engine(os.getenv("DB_URL"))
Session = sessionmaker()


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    id = factory.Sequence(lambda n: -n)
    nickname = factory.Sequence(lambda n: u'_user_{}'.format(n))
    tg_id = factory.Sequence(lambda n: -n - 1000)

    class Meta:
        model = dal.User


class ChannelFactory(factory.alchemy.SQLAlchemyModelFactory):
    id = factory.Sequence(lambda n: -n)
    title = factory.Sequence(lambda n: u'_channel_{}'.format(n))
    tg_id = factory.Sequence(lambda n: -n - 1000)

    class Meta:
        model = dal.Channel


class SubscriptionFactory(factory.alchemy.SQLAlchemyModelFactory):
    id = factory.Sequence(lambda n: -n)
    channel_id = factory.LazyAttribute(lambda o: o.channel.id)
    user_id = factory.LazyAttribute(lambda o: o.user.id)

    user = factory.SubFactory(UserFactory)
    channel = factory.SubFactory(ChannelFactory)

    class Meta:
        model = dal.Subscription


def patch_factories(fc_classes, session):
    for factory_cls in fc_classes:
        if factory_cls.__class__ is not factory.base.FactoryMetaClass:
            continue
        factory_cls._meta.sqlalchemy_session = session


@pytest.fixture(scope='module')
def connection():
    connection = engine.connect()
    yield connection
    connection.close()


@pytest.fixture(scope='function')
def session(connection):
    transaction = connection.begin()
    session = Session(bind=connection)
    patch_factories(
        (UserFactory, ChannelFactory, SubscriptionFactory),
        session
    )
    yield session
    session.close()
    transaction.rollback()


def test_user_deletion(session):
    user = UserFactory.create()
    assert session.query(dal.User).filter(dal.User.id == user.id).one()

    store = Store(session)
    store.delete_user(user_id=user.id)

    result = session.query(dal.User).filter(dal.User.id == user.id).one_or_none()
    assert result is None


def test_user_creation(session):
    store = Store(session)
    created_user = store.create_user(nickname="_user1", tg_id=-123)
    user = session.query(dal.User).filter(
        dal.User.id == created_user.id
    ).one_or_none()

    assert user is not None
    assert user.nickname == "_user1"
    assert user.tg_id == -123


def test_user_existence(session):
    store = Store(session)
    user = UserFactory.create()

    assert store.user_exists(user_id=user.id)
    assert store.user_exists(tg_id=user.tg_id)
    assert store.user_exists(nickname=user.nickname)
    assert not store.user_exists(user_id=-123)


def test_user_getting(session):
    store = Store(session)
    users = UserFactory.create_batch(5)

    user_ids = [user.id for user in users[:3]]
    fetched_users = store.get_users(user_ids=user_ids)
    fetched_ids = [user.id for user in fetched_users]
    assert sorted(fetched_ids) == sorted(user_ids)

    tg_ids = [user.tg_id for user in users[:3]]
    fetched_users = store.get_users(tg_ids=tg_ids)
    fetched_ids = [user.id for user in fetched_users]
    assert sorted(fetched_ids) == sorted(user_ids)

    nicknames = [user.nickname for user in users[:3]]
    fetched_users = store.get_users(nicknames=nicknames)
    fetched_ids = [chan.id for chan in fetched_users]
    assert sorted(fetched_ids) == sorted(user_ids)

    user_ids = [user.id for user in users]
    fetched_users = store.get_users()
    fetched_ids = [user.id for user in fetched_users]
    filtered_ids = [user_id for user_id in fetched_ids if user_id in user_ids]
    assert sorted(filtered_ids) == sorted(user_ids)


def test_channel_deletion(session):
    chan = ChannelFactory.create()
    assert session.query(dal.Channel).filter(dal.Channel.id == chan.id).one()

    store = Store(session)
    store.delete_channel(chan_id=chan.id)

    result = session.query(dal.Channel).filter(
        dal.Channel.id == chan.id
    ).one_or_none()
    assert result is None


def test_channel_creation(session):
    store = Store(session)
    created_chan = store.create_channel(title="_channel1", tg_id=-123)
    chan = session.query(dal.Channel).filter(
        dal.Channel.id == created_chan.id
    ).one_or_none()

    assert chan is not None
    assert chan.title == "_channel1"
    assert chan.tg_id == -123


def test_channel_existence(session):
    store = Store(session)
    chan = ChannelFactory.create()

    assert store.channel_exists(channel_id=chan.id)
    assert store.channel_exists(tg_id=chan.tg_id)
    assert store.channel_exists(title=chan.title)
    assert not store.channel_exists(channel_id=-123)


def test_channel_getting(session):
    store = Store(session)
    chans = ChannelFactory.create_batch(5)

    chan_ids = [chan.id for chan in chans[:3]]
    fetched_chans = store.get_channels(chan_ids=chan_ids)
    fetched_ids = [chan.id for chan in fetched_chans]
    assert sorted(fetched_ids) == sorted(chan_ids)

    tg_ids = [chan.tg_id for chan in chans[:3]]
    fetched_chans = store.get_channels(tg_ids=tg_ids)
    fetched_ids = [chan.id for chan in fetched_chans]
    assert sorted(fetched_ids) == sorted(chan_ids)

    titles = [chan.title for chan in chans[:3]]
    fetched_chans = store.get_channels(titles=titles)
    fetched_ids = [chan.id for chan in fetched_chans]
    assert sorted(fetched_ids) == sorted(chan_ids)

    chan_ids = [chan.id for chan in chans]
    fetched_chans = store.get_channels()
    fetched_ids = [chan.id for chan in fetched_chans]
    filtered_ids = [chan_id for chan_id in fetched_ids if chan_id in chan_ids]
    assert sorted(filtered_ids) == sorted(chan_ids)


def test_subscription_creation(session):
    store = Store(session)
    user = UserFactory.create()
    chan = ChannelFactory.create()

    created_sub = store.create_subscription(user_id=user.id, channel_id=chan.id)
    sub = session.query(dal.Subscription).filter(
        dal.Subscription.id == created_sub.id
    ).one_or_none()

    assert sub is not None
    assert sub.channel.id == chan.id
    assert sub.user.id == user.id

    with pytest.raises(Exception):
        store.create_subscription(-123, None)

    with pytest.raises(Exception):
        store.create_subscription(None, -123)


def test_subscription_existence(session):
    store = Store(session)
    sub = SubscriptionFactory.create()

    assert store.subscription_exists(
        user_id=sub.user.id,
        channel_id=sub.channel.id
    )
    assert not store.subscription_exists(user_id=-123, channel_id=-456)

    with pytest.raises(Exception):
        store.subscription_exists(user_id=-123)

    with pytest.raises(Exception):
        store.subscription_exists(channel_id=-123)


def test_subscription_getting(session):
    store = Store(session)
    subs = SubscriptionFactory.create_batch(5)

    sub_ids = [sub.id for sub in subs[:3]]
    fetched_subs = store.get_subscriptions(sub_ids=sub_ids)
    fetched_ids = [sub.id for sub in fetched_subs]
    assert sorted(fetched_ids) == sorted(sub_ids)

    chan_ids = [sub.channel.id for sub in subs[:3]]
    fetched_subs = store.get_subscriptions(channel_ids=chan_ids)
    fetched_ids = [sub.channel.id for sub in fetched_subs]
    assert sorted(fetched_ids) == sorted(chan_ids)

    user_ids = [sub.user.id for sub in subs[:3]]
    fetched_subs = store.get_subscriptions(user_ids=user_ids)
    fetched_ids = [sub.user.id for sub in fetched_subs]
    assert sorted(fetched_ids) == sorted(user_ids)

    sub_ids = [sub.id for sub in subs]
    fetched_subs = store.get_subscriptions()
    fetched_ids = [sub.id for sub in fetched_subs]
    filtered_ids = [sub_id for sub_id in fetched_ids if sub_id in sub_ids]
    assert sorted(filtered_ids) == sorted(sub_ids)


def test_prepare_args_for_multiple_select():
    args = ["arg1", "arg2", None, "arg3"]
    kwargs = {"1kwarg": "val1", "2kwarg": "val2"}
    args, kwargs = Store._prepare_args_for_multiple_select(args, kwargs)
    assert args == [["arg1"], ["arg2"], None, ["arg3"]]
    assert kwargs == {"1kwargs": ["val1"], "2kwargs": ["val2"]}
