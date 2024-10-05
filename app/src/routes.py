from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Request,
    Response,
    UploadFile,
)
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database import engine, get_db
from src.models import (
    Base,
    User,
    add_following,
    add_like,
    add_media,
    add_tweet,
    add_user,
    create_data,
    get_all_tweets,
    get_like,
    get_media,
    get_profile,
    get_tweet_by_id,
    get_user_by_apikey,
    remove_following,
    sorted_tweets,
)
from src.schemas import (
    AddMediaOut,
    AllTweetsOut,
    StandartResponse,
    TweetIn,
    TweetOut,
    UserIn,
    UserOut,
    UserProfileResponse,
)

router = APIRouter()


@router.post("/api/users", status_code=201, response_model=UserOut)
async def get_user_handler(user_data: UserIn, db: AsyncSession = Depends(get_db)):
    """Создает нового пользователя"""
    try:
        user = await add_user(db=db, **vars(user_data))
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="a user with such data already exists"
        )
    return user


@router.post("/api/tweets", response_model=TweetOut, status_code=201)
async def add_tweet_handler(
    request: Request, tweet_data: TweetIn, db: AsyncSession = Depends(get_db)
):
    """Добавить твит и получить id"""
    headers = request.headers
    api_key = headers["api-key"]

    user = await get_user_by_apikey(db=db, api_key=api_key)
    user_id = user.id

    tweet = await add_tweet(db=db, user_id=user_id, **vars(tweet_data))

    if not tweet:
        raise HTTPException(status_code=400, detail="error")

    result = {"result": True, "tweet_id": tweet.id}
    return result


@router.post("/api/medias", status_code=201, response_model=AddMediaOut)
async def add_media_handler(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
):
    """Добавить медиа и получить id"""
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="invalid file type")

    filename = file.filename
    data = await file.read()
    mimetype = file.content_type

    media = await add_media(db=db, filename=filename, data=data, mimetype=mimetype)
    result = {"result": True, "media_id": media.id}
    return result


@router.delete("/api/tweets/{id}", response_model=StandartResponse)
async def delete_tweet_handler(
    id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    """Удаляет твит если его создал пользовтель, который отправил запрос на удаление"""
    headers = request.headers
    api_key = headers["api-key"]

    user = await get_user_by_apikey(db=db, api_key=api_key)
    tweet = await get_tweet_by_id(db=db, tweet_id=id)

    if not user:
        raise HTTPException(status_code=400, detail="user not found")
    elif not tweet:
        raise HTTPException(status_code=400, detail="tweet not found")
    elif not tweet.user_id == user.id:
        raise HTTPException(status_code=400, detail="no right to delete")

    await db.delete(tweet)
    await db.commit()

    return {"result": True}


@router.post("/api/tweets/{id}/likes", status_code=201, response_model=StandartResponse)
async def add_like_handler(
    id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    """Поставить лайк на твит"""
    headers = request.headers
    api_key = headers["api-key"]

    user = await get_user_by_apikey(db=db, api_key=api_key)
    tweet = await get_tweet_by_id(db=db, tweet_id=id)

    if not user:
        raise HTTPException(status_code=400, detail="user not found")
    elif not tweet:
        raise HTTPException(status_code=400, detail="tweet not found")

    like = await add_like(db=db, tweet_id=tweet.id, user_id=user.id)

    if not like:
        raise HTTPException(status_code=400, detail="like already exists")

    return {"result": True}


@router.delete("/api/tweets/{id}/likes", response_model=StandartResponse)
async def remove_like_handler(
    id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    """Убрать лайк с твита"""
    headers = request.headers
    api_key = headers["api-key"]

    user = await get_user_by_apikey(db=db, api_key=api_key)
    tweet = await get_tweet_by_id(db=db, tweet_id=id)

    if not user:
        raise HTTPException(status_code=400, detail="user not found")
    elif not tweet:
        raise HTTPException(status_code=400, detail="tweet not found")

    like = await get_like(db=db, tweet_id=tweet.id, user_id=user.id)

    if not like:
        raise HTTPException(status_code=400, detail="like not found")

    await db.delete(like)
    await db.commit()
    return {"result": True}


@router.post("/api/users/{id}/follow", status_code=201, response_model=StandartResponse)
async def add_following_handler(
    id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    """Добавляет подписку на пользователя"""
    headers = request.headers
    api_key = headers["api-key"]

    follower = await get_user_by_apikey(db=db, api_key=api_key)
    followee = await db.execute(select(User).where(User.id == id))
    followee = followee.scalar()

    if not follower:
        raise HTTPException(status_code=400, detail="follower not found")
    elif not followee:
        raise HTTPException(status_code=400, detail="followee not found")

    following = await add_following(
        db=db, user_follower_id=follower.id, user_followee_id=followee.id
    )

    if not following:
        raise HTTPException(status_code=400, detail="following already exists")

    return {"result": True}


@router.delete("/api/users/{id}/follow", response_model=StandartResponse)
async def remove_following_handler(
    id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    """Убирает подписку на пользователя"""
    headers = request.headers
    api_key = headers["api-key"]

    follower = await get_user_by_apikey(db=db, api_key=api_key)
    followee = await db.execute(select(User).where(User.id == id))
    followee = followee.scalar()

    if not follower:
        raise HTTPException(status_code=400, detail="follower not found")
    elif not followee:
        raise HTTPException(status_code=400, detail="followee not found")

    following = await remove_following(
        db=db, user_follower_id=follower.id, user_followee_id=followee.id
    )

    if not following:
        raise HTTPException(status_code=400, detail="following not found")

    return {"result": True}


@router.get("/api/tweets", response_model=AllTweetsOut)
async def get_all_tweets_handler(request: Request, db: AsyncSession = Depends(get_db)):
    """Выдает все твиты"""
    headers = request.headers
    api_key = headers["api-key"]

    user = await get_user_by_apikey(db=db, api_key=api_key)

    if not user:
        raise HTTPException(status_code=400, detail="user not found")

    user_profile = await get_profile(db=db, id=user.id, name=user.name)
    followings_data = user_profile["following"]
    if not followings_data:
        followings_ids = []
    else:
        followings_ids = [data["id"] for data in followings_data]
    tweets = await get_all_tweets(db=db)
    sorted_tweets_list = await sorted_tweets(
        following_ids=followings_ids, db=db, tweets=tweets
    )

    result = {"result": True, "tweets": sorted_tweets_list}

    return result


@router.get("/api/users/me", response_model=UserProfileResponse)
async def get_my_profile_handler(request: Request, db: AsyncSession = Depends(get_db)):
    """Выводит профиль пользователя, который сделал запрос"""
    headers = request.headers
    api_key = headers["api-key"]

    user = await get_user_by_apikey(db=db, api_key=api_key)

    if not user:
        raise HTTPException(status_code=400, detail="user not found")

    user_profile = await get_profile(db=db, id=user.id, name=user.username)
    result = {"result": True, "user": user_profile}
    return result


@router.get("/api/users/{id}", response_model=UserProfileResponse)
async def get_user_profile_handler(id: int, db: AsyncSession = Depends(get_db)):
    """Выводит профиль пользователя по id"""

    user_sql = await db.execute(select(User).where(User.id == id))
    user = user_sql.scalar()

    if not user:
        raise HTTPException(status_code=400, detail="user not found")

    user_profile = await get_profile(db=db, id=user.id, name=user.username)
    result = {"result": True, "user": user_profile}
    return result


@router.get("/api/medias/{id}")
async def get_media_handler(id: int, db: AsyncSession = Depends(get_db)):
    """Выдает медиафайл по id"""
    media = await get_media(db=db, id=id)
    return Response(content=media, media_type="image/jpeg")


@router.get("/api/content/create")
async def create_data_handler(db: AsyncSession = Depends(get_db)):
    """Наполняет БД данными, для призентации"""
    await create_data(db=db)
    return {"result": True}


@router.get("/api/content/delete")
async def drop_all_tables(db: AsyncSession = Depends(get_db)):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.execute(text("DROP TABLE IF EXISTS alembic_version;"))

        return {"result": True, "message": "all tables dropped from database"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
