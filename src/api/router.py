from datetime import datetime, date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from src.api.schema import UserDataSchema
from src.core.db import SessionAnnotated
from src.core.paginator import Paginator, EmptyPage
from src.models.model import UserData

user_router = APIRouter()


@user_router.post("/create")
async def post_user(session: SessionAnnotated, schema: UserDataSchema):
    user_data = UserData(
        time_create=schema.time_create,
        time_insure_end=schema.time_insure_end,
        first_name=schema.first_name.capitalize(),
        middle_name=schema.middle_name.capitalize(),
        last_name=schema.last_name.capitalize(),
        phone=schema.phone,
        email=schema.email
    )
    try:
        session.add(user_data)
        await session.commit()
    except Exception as exp:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exp))

    return {"message": "Пользователь создан успешно"}


@user_router.get("/{user_id}")
async def get_user(session: SessionAnnotated, user_id: int):
    user_query = await session.execute(select(UserData).where(UserData.id == user_id))
    user = user_query.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user.to_dict()


@user_router.put("/{user_id}")
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


@user_router.get("/get_all/")
async def get_all_user(session: SessionAnnotated,
                       date_insurance_end: Optional[date] = Query(None),
                       phone_number: Optional[str] = Query(None),
                       limit: int = 10,
                       page: int = 1
                       ):
    query = select(UserData)

    if date_insurance_end is not None:
        query = query.filter(UserData.time_insure_end <= date_insurance_end)
    if phone_number is not None:
        query = query.filter(UserData.phone.like(f"%{phone_number}%"))

    result = await session.execute(query)
    user_data = result.scalars().all()

    if not user_data:
        raise HTTPException(status_code=404, detail="Users not found")

    paginator = Paginator(user_data, limit)

    try:
        page_data = paginator.page(page)
    except EmptyPage:
        raise HTTPException(status_code=404, detail="This page contains no results")

    users_data = [user.to_dict() for user in page_data.object_list]

    return {
        "total": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": page,
        "data": users_data
    }


@user_router.delete("/{user_id}")
async def delete_user(session: SessionAnnotated, user_id: int):
    user_query = await session.execute(select(UserData).where(UserData.id == user_id))
    user = user_query.scalars().first()
    await session.delete(user)
    await session.commit()
    if user_query is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Пользователь удален успешно"}
