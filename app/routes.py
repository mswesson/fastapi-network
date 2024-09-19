from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import User, add_tweet, add_media
from app.schemas import TweetIn, TweetOut

router = APIRouter()


@router.get("/tweets")
async def view_all_tweets_handler(db: AsyncSession = Depends(get_db)):
    """Вывести всех пользователей"""
    result = await db.execute(select(User))
    result = result.scalars().all()
    return result


@router.post("/api/tweets", response_model=TweetOut, status_code=201)
async def add_tweet_handler(tweet_data: TweetIn, db: AsyncSession = Depends(get_db)):
    """Добавить твит и получить id"""
    user_id = 1
    text = tweet_data.tweet_data
    media = tweet_data.tweet_media_ids
    tweet = await add_tweet(db=db, user_id=user_id, text=text, media=media)
    result = {"result": True, "tweet_id": tweet.id}
    return result


@router.post("/api/medias", status_code=201)
async def add_media_handler(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
):
    """Добавить медиа и получить id"""
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    filename = file.filename
    data = await file.read()
    mimetype = file.content_type

    media = await add_media(db=db, filename=filename, data=data, mimetype=mimetype)
    result = {"result": True, "media_id": media.id}
    return result
