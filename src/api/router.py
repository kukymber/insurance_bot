from datetime import datetime

from fastapi import APIRouter, HTTPException, FastAPI
from sqlalchemy import select

from src.api.schema import UserDataSchema
from src.core.db import SessionAnnotated
from src.core.paginator import Paginator, EmptyPage
from src.models.model import UserData

user_router = APIRouter()


@user_router.post("/create", response_model=UserData)
async def post_user(session: SessionAnnotated, schema: UserDataSchema):
    user_data = UserData(**schema.dict())
    try:
        session.add(user_data)
        await session.commit()
    except Exception as exp:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exp))

    return {"message": "Пользователь создан успешно"}


@user_router.get("/{user_id}", response_model=UserData)
async def get_user(session: SessionAnnotated, user_id: int):
    user_query = await session.execute(select(UserData).where(UserData.id == user_id)).fetchone()
    if user_query is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user_query.to_dict()


@user_router.put("/{user_id}", response_model=UserData)
async def update_user(session: SessionAnnotated, user_id: int, schema: UserDataSchema):
    user = await session.execute(select(UserData).where(UserData.id == user_id))
    user = user.scalars().first()

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    for var, value in schema.dict(exclude_unset=True).items():
        setattr(user, var, value)
    session.add(user)
    await session.commit()
    return HTTPException(status_code=200, detail="Данные пользователя успешно обновлены")


@user_router.get("/get_all", response_model=UserData)
async def get_all_user(session: SessionAnnotated, user_id: int = None, date_insurance_end: datetime = None,
                       phone_number: str = None, limit: int = 10, page: int = 1):
    query = select(UserData)

    if user_id is not None:
        query = query.filter(UserData.id == user_id)
    if date_insurance_end is not None:
        query = query.filter(UserData.time_insure_end <= date_insurance_end)
    if phone_number is not None:
        query = query.filter(UserData.phone == phone_number)

    result = await session.execute(query)
    user_data = result.scalars().all()

    if not user_data:
        raise HTTPException(status_code=404, detail="Users not found")

    paginator = Paginator(user_data, limit)

    try:
        page_data = paginator.page(page)
    except EmptyPage:
        raise HTTPException(status_code=404, detail="This page contains no results")

    users_data = [user.to_dict() for user in
                  page_data.object_list]

    return {
        "total": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": page,
        "data": users_data
    }


@user_router.delete("/{user_id}", response_model=UserData)
async def delete_user(session: SessionAnnotated, user_id: int):
    user_query = session.execute(select(UserData).where(UserData.id == user_id)).fetchone()
    session.delete(user_query)
    await session.commit()
    if user_query is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_query

