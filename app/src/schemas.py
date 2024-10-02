from typing import List, Optional

from pydantic.main import BaseModel


class TweetIn(BaseModel):
    """3.0 Схема запроса на добавление твита"""

    tweet_data: str
    tweet_media_ids: List[Optional[int]]


class TweetOut(BaseModel):
    """3.0 Схема ответа, при добавлении твита или неудаче"""

    result: bool
    tweet_id: Optional[int]


class AuthorToAllTweets(BaseModel):
    """2.3 Автор для вывода всех твитов"""

    id: int
    name: str


class LikesToAllTweets(BaseModel):
    """2.2 Лайк для вывода всех твитов"""

    user_id: int
    name: str


class Tweet(BaseModel):
    """2.1 Основной твит, содержит в себе все данные"""

    id: int
    content: str
    attachments: List[Optional[str]]
    author: AuthorToAllTweets
    likes: List[Optional[LikesToAllTweets]]


class AllTweetsOut(BaseModel):
    """2.0 Схема ответа, при выводе всех твитов"""

    result: bool
    tweets: List[Optional[Tweet]]


class UserIn(BaseModel):
    """4.0 Добавление пользователя"""

    api_key: str
    username: str
    name: str
    surname: str


class UserOut(BaseModel):
    """4.0 Ответ сервера с юзером"""

    id: int
    api_key: str
    username: str
    name: str
    surname: str


class FollowToUserProfile(BaseModel):
    """1.2 Список подписчиков или подписок для ответа на профиль пользователя"""

    id: int
    name: str


class UserToUserProfile(BaseModel):
    """1.1 Пользователь для ответа на профиль пользователя"""

    id: int
    name: str
    followers: List[Optional[FollowToUserProfile]]
    following: List[Optional[FollowToUserProfile]]


class UserProfileResponse(BaseModel):
    """1.0 Ответ на профиль пользователя"""

    result: bool
    user: UserToUserProfile


class AddMediaOut(BaseModel):
    """Добавление медиа входная схема"""

    result: bool
    media_id: int


class StandartResponse(BaseModel):
    """Стандартный ответ показывающий статус запроса"""

    result: bool
