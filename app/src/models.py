from random import randint
from typing import Optional

from sqlalchemy import (
    ARRAY,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    UniqueConstraint,
    select,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, selectinload
from src.database import Base
from src.test_user_data import TEST_TWEETS_DATA, TEST_USER_DATA


class Follower(Base):
    __tablename__ = "followers"

    id = Column(Integer, primary_key=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    followee_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    follower = relationship(
        "User", foreign_keys=[follower_id], back_populates="following"
    )
    followee = relationship(
        "User", foreign_keys=[followee_id], back_populates="followers"
    )

    __table_args__ = (
        UniqueConstraint("follower_id", "followee_id", name="uq_follower_followee"),
        CheckConstraint("follower_id != followee_id", name="chk_follower_not_self"),
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)

    tweets = relationship("Tweet", back_populates="user")
    likes = relationship("Like", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    followers = relationship(
        "Follower", foreign_keys=[Follower.followee_id], back_populates="followee"
    )  # Те на кого подписан пользователь
    following = relationship(
        "Follower", foreign_keys=[Follower.follower_id], back_populates="follower"
    )  # Те кто подписан на пользователя


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(String, nullable=False)
    media = Column("my_array", ARRAY(Integer), nullable=True)

    user = relationship("User", back_populates="tweets")
    likes = relationship("Like", back_populates="tweet")
    comments = relationship("Comment", back_populates="tweet")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=False)

    user = relationship("User", back_populates="likes")
    tweet = relationship("Tweet", back_populates="likes")

    __table_args__ = (UniqueConstraint("user_id", "tweet_id", name="uq_user_tweet"),)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=False)
    text = Column(String, nullable=False)

    user = relationship("User", back_populates="comments")
    tweet = relationship("Tweet", back_populates="comments")


class Media(Base):
    __tablename__ = "medias"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    data = Column(LargeBinary, nullable=False)
    mimetype = Column(String, nullable=False)


async def add_tweet(
    db: AsyncSession, user_id: int, tweet_data: str, tweet_media_ids: int = None
) -> Optional[Tweet]:
    """Добавляет новый твит"""

    if not tweet_media_ids:
        tweet_media_ids = None

    tweet = Tweet(
        user_id=user_id,
        text=tweet_data,
        media=tweet_media_ids,
    )
    db.add(tweet)
    await db.commit()
    await db.refresh(tweet)
    return tweet


async def add_user(
    db: AsyncSession, api_key: str, username: str, name: str, surname: str
) -> User:
    """Добавляет нового пользователя"""
    user = User(
        api_key=api_key,
        username=username,
        name=name,
        surname=surname,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def add_media(
    db: AsyncSession, filename: str, data: bytes, mimetype: str
) -> Optional[Media]:
    """Добавляет медиа"""
    media = Media(filename=filename, data=data, mimetype=mimetype)
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media


async def get_user_by_apikey(db: AsyncSession, api_key: str) -> User:
    """Выдает пользователя по apikey"""
    user = await db.execute(select(User).where(User.api_key == api_key))
    user = user.scalars().first()
    return user


async def get_tweet_by_id(db: AsyncSession, tweet_id: int) -> Tweet:
    """Выдает твит по id"""
    tweet = await db.execute(select(Tweet).where(Tweet.id == tweet_id))
    tweet = tweet.scalar()
    return tweet


async def add_like(db: AsyncSession, tweet_id: int, user_id: int) -> Optional[Like]:
    """Создает лайк"""
    like = Like(tweet_id=tweet_id, user_id=user_id)
    try:
        db.add(like)
        await db.commit()
        await db.refresh(like)
    except IntegrityError:
        return None
    return like


async def get_like(db: AsyncSession, tweet_id: int, user_id: int) -> Like:
    like = await db.execute(
        select(Like).where(Like.tweet_id == tweet_id, Like.user_id == user_id)
    )
    like = like.scalar()
    return like


async def add_following(
    db: AsyncSession, user_follower_id: int, user_followee_id: int
) -> Follower:
    """
    Добавляет подписку на юзера

    Атрибуты:
        user_follower_id (int): юзер, который подписывается на друго юзера
        user_followee_id (int): юзер, на которого подписался другой юзер
    """
    try:
        follower = Follower(follower_id=user_follower_id, followee_id=user_followee_id)
        db.add(follower)
        await db.commit()
        await db.refresh(follower)
    except IntegrityError:
        return None
    return follower


async def remove_following(
    db: AsyncSession, user_follower_id: int, user_followee_id: int
) -> Follower:
    """
    Убирает подписку на юзера

    Атрибуты:
        user_follower_id (int): юзер, который подписан на друго юзера
        user_followee_id (int): юзер, на которого подписан другой юзер
    """
    follower = await db.execute(
        select(Follower).where(
            Follower.follower_id == user_follower_id,
            Follower.followee_id == user_followee_id,
        )
    )
    follower = follower.scalar()

    if not follower:
        return None

    await db.delete(follower)
    await db.commit()
    return follower


async def get_all_tweets(db: AsyncSession) -> list:
    """Выводит все твиты согласно схемы из ТЗ"""
    tweets_result = await db.execute(
        select(Tweet).options(
            selectinload(Tweet.user), selectinload(Tweet.likes).selectinload(Like.user)
        )
    )
    tweets = tweets_result.scalars().all()
    result = []

    for tweet in tweets:
        likes = tweet.likes
        likes_data = []

        if not tweet.media:
            attachments = []
        else:
            attachments = [f"/api/medias/{media_id}" for media_id in tweet.media]

        if likes:
            for like in likes:
                like_data = {"user_id": like.user.id, "name": like.user.username}
                likes_data.append(like_data)

        tweet_data = {
            "id": tweet.id,
            "content": tweet.text,
            "attachments": attachments,
            "author": {"id": tweet.user.id, "name": tweet.user.username},
            "likes": likes_data,
        }

        result.append(tweet_data)
    return result


async def sorted_tweets(db: AsyncSession, following_ids: list, tweets: list):
    """
    Сортирует твиты по принципу - сначала идут твиты тех, на кого подписан пользователь,
    отсортированные по количеству лайков

    Атрибуты:
        db: сессия базы данных
        following_ids (list): список id подписок
        tweets (list): список твитов в формате Tweet из schemas.py
    """
    if not following_ids:
        result = sorted(tweets, key=lambda x: len(x["likes"]), reverse=True)
        return result

    tweets_is_following = [
        tweet for tweet in tweets if tweet["author"]["id"] in following_ids
    ]
    tweets_is_not_following = [
        tweet for tweet in tweets if tweet["author"]["id"] not in following_ids
    ]

    sorted_tweets_is_following = sorted(
        tweets_is_following, key=lambda x: len(x["likes"]), reverse=True
    )
    sorted_tweets_is_not_following = sorted(
        tweets_is_not_following, key=lambda x: len(x["likes"]), reverse=True
    )
    merge_list_tweets = sorted_tweets_is_following + sorted_tweets_is_not_following
    return merge_list_tweets


async def get_profile(db: AsyncSession, id: int, name: str):
    """Выдает профиль пользователя согласно схеме из ТЗ"""
    followers = await db.execute(
        select(Follower)
        .where(Follower.followee_id == id)
        .options(selectinload(Follower.follower))
    )
    followees = await db.execute(
        select(Follower)
        .where(Follower.follower_id == id)
        .options(selectinload(Follower.followee))
    )
    followers = followers.scalars().all()
    followees = followees.scalars().all()
    followers = [
        {"id": follower.follower.id, "name": follower.follower.name}
        for follower in followers
    ]
    followees = [
        {"id": followee.followee.id, "name": followee.followee.name}
        for followee in followees
    ]

    result = {
        "id": id,
        "name": name,
        "followers": followers,
        "following": followees,
    }

    return result


async def get_media(db: AsyncSession, id: int):
    """Выдает медиа файл по id"""
    media_res = await db.execute(select(Media.data).where(Media.id == id))
    media = media_res.scalar()
    return media


async def create_data(db: AsyncSession):
    """Наполняет БД данными для призентации"""
    users = []
    tweets = []
    likes = []
    followings = []

    # Users
    for name, surname, username, api_key in TEST_USER_DATA:
        user = User(name=name, surname=surname, username=username, api_key=api_key)
        users.append(user)

    # Tweets
    for text in TEST_TWEETS_DATA:
        tweet = Tweet(user_id=randint(1, 20), text=text)
        tweets.append(tweet)

    # Likes
    for user_id in range(1, 21):
        like = Like(user_id=user_id, tweet_id=randint(1, 40))
        likes.append(like)

    # Followings
    for follower_id in range(1, 21):
        followee_id = randint(1, 20)

        if followee_id == follower_id:
            if followee_id == 20:
                followee_id -= 1
            else:
                followee_id += 1

        following = Follower(follower_id=follower_id, followee_id=followee_id)
        followings.append(following)

    db.add_all(users)
    await db.commit()
    db.add_all(tweets)
    await db.commit()
    db.add_all(likes)
    await db.commit()
    db.add_all(followings)
    await db.commit()
