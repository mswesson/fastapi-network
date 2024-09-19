from sqlalchemy import Column, ForeignKey, Integer, String, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)

    tweets = relationship("Tweet", back_populates="user")
    likes = relationship("Like", back_populates="user")
    comments = relationship("Comment", back_populates="user")


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(String, nullable=False)
    media = Column(Integer, nullable=True)

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
    db: AsyncSession, user_id: int, text: str, media: int = None
) -> Optional[Tweet]:
    """Добавляет новый твит"""
    tweet = Tweet(
        user_id=user_id,
        text=text,
        media=media,
    )
    db.add(tweet)
    await db.commit()
    await db.refresh(tweet)
    return tweet


async def add_user(
    db: AsyncSession, token: str, username: str, name: str, surname: str
) -> User:
    """Добавляет нового пользователя"""
    user = User(
        token=token,
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
