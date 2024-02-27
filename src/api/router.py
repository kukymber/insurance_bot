from datetime import datetime, date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from src.api.schema import UserDataSchema
from src.core.db import SessionAnnotated
from src.core.paginator import Paginator, EmptyPage
from src.models.model import UserData, InsuranceInfo

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
    session.add(user_data)
    await session.flush()
    polis_info = InsuranceInfo(
        description=schema.description,
        polis_type=schema.polis_type,
        polis_extended=schema.polis_extended,
        user_id=user_data.id,
    )
    session.add(polis_info)
    try:
        await session.commit()
    except Exception as exp:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exp))

    return {"message": "Пользователь создан успешно"}


@user_router.get("/{user_id}")
async def get_user(session: SessionAnnotated, user_id: int):
    user_query = await session.execute(select(UserData).where(UserData.id == user_id))
    user = user_query.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user.to_dict()


@user_router.put("/{user_id}")
async def update_user(session: SessionAnnotated, user_id: int, schema: UserDataSchema):
    user = await session.execute(select(UserData).where(UserData.id == user_id))
    user = user.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    for var, value in schema.dict(exclude_unset=True).items():
        if var in ['first_name', 'middle_name', 'last_name']:
            value = value.capitalize()
        setattr(user, var, value)
    session.add(user)
    await session.commit()
    return HTTPException(status_code=200, detail="Данные пользователя успешно обновлены")


@user_router.get("/get_all/")
async def get_all_user(session: SessionAnnotated,
                       date_insurance_end: Optional[date] = Query(None),
                       search_query: Optional[str] = Query(None)):
    query = select(UserData)

    if date_insurance_end:
        query = query.filter(UserData.time_insure_end <= date_insurance_end)
    if search_query:
        if search_query.isdigit():
            query = query.filter(UserData.phone.like(f"%{search_query}%"))
        else:
            parts = search_query.split('+')
            surname = parts[0]
            query = query.filter(UserData.last_name.like(f"{surname}%"))
            if len(parts) > 1:
                name = parts[1]
                query = query.filter(UserData.first_name.like(f"{name}%"))
            if len(parts) > 2:
                patronymic = parts[2]
                query = query.filter(UserData.middle_name.like(f"{patronymic}%"))

    result = await session.execute(query)
    user_data = result.scalars().all()

    if not user_data:
        raise HTTPException(status_code=404, detail="Users not found")

    users_data = [user.to_dict() for user in user_data]

    return users_data


@user_router.delete("/{user_id}")
async def delete_user(session: SessionAnnotated, user_id: int):
    user_query = await session.execute(select(UserData).where(UserData.id == user_id))
    user = user_query.scalars().first()
    await session.delete(user)
    await session.commit()
    if user_query:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Пользователь удален успешно"}
