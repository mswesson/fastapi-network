from pydantic.main import BaseModel
from pydantic import Field
from typing import Optional, List


class TweetIn(BaseModel):
    """Схема запроса на добавление твита"""

    tweet_data: str
    tweet_media_ids: Optional[List[int]]


class TweetOut(BaseModel):
    """Схема ответа, при добавлении твита или неудаче"""

    result: bool
    tweet_id: Optional[int]
