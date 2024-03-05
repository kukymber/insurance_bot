from datetime import datetime
from typing import Optional, List

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from src.api.schema import UserDataSchema
from src.core.db import SessionAnnotated
from src.core.paginator import Paginator
from src.models.model import UserData, InsuranceInfo

user_router = APIRouter()


@user_router.post("/create")
async def post_user(session: SessionAnnotated, schema: UserDataSchema):
    user = UserData(
        time_create=schema.time_create,
        first_name=schema.first_name.capitalize(),
        middle_name=schema.middle_name.capitalize(),
        last_name=schema.last_name.capitalize(),
        phone=schema.phone,
        email=schema.email
    )
    session.add(user)
    await session.flush()
    polis_info = InsuranceInfo(
        description=schema.description,
        polis_type=schema.polis_type,
        polis_extended=schema.polis_extended,
        time_insure_end=schema.time_insure_end,
        user_id=user.id,
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
    polis = await session.execute(select(InsuranceInfo).where(InsuranceInfo.user_id == user_id))
    polis = polis.scalars().first()
    if not user or not polis:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {**user.to_dict(), **polis.to_dict()}


@user_router.put("/{user_id}")
async def update_user(session: SessionAnnotated, user_id: int, schema: UserDataSchema):
    user = await session.execute(select(UserData).where(UserData.id == user_id))
    user = user.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    for var, value in schema.dict(exclude_unset=True).items():
        setattr(user, var, value.capitalize() if var in ['first_name', 'middle_name', 'last_name'] else value)

    polis = await session.execute(select(InsuranceInfo).where(InsuranceInfo.user_id == user_id))
    polis = polis.scalars().first()

    if polis:
        for var, value in schema.dict(exclude_unset=True, exclude_none=True).items():
            setattr(polis, var, value)
    else:
        raise HTTPException(status_code=404, detail="Данные о полисе пользователя не найдены")

    session.add(user)
    session.add(polis)

    try:
        await session.commit()
    except Exception as exp:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exp))

    return {"message": "Пользователь и его полис обновлены успешно"}


@user_router.get("/get_all/")
async def get_all_user(session: SessionAnnotated,
                       date_insurance_end: Optional[str] = Query(None),
                       search_query: Optional[str] = Query(None),
                       page_number: int = Query(1, alias="page"),
                       page_size: int = Query(10, alias="size")
                       ):
    if date_insurance_end:
        end_date = datetime.fromisoformat(date_insurance_end).date()
        start_date = end_date - relativedelta(months=2)
        query = select(InsuranceInfo).join(UserData, UserData.id == InsuranceInfo.user_id).filter(
            InsuranceInfo.time_insure_end >= start_date,
            InsuranceInfo.time_insure_end <= end_date
        )
    else:
        query = select(UserData).join(InsuranceInfo, UserData.id == InsuranceInfo.user_id)
        if search_query:
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

    paginator = Paginator(user_data, page_size)
    page = paginator.page(page_number)

    return {
        "total": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": page.number,
        "users": [user.to_dict() for user in page.object_list]
    }


@user_router.delete("/{user_id}")
async def delete_user(session: SessionAnnotated, user_id: int):
    user_query = await session.execute(select(UserData).where(UserData.id == user_id))
    user = user_query.scalars().first()
    await session.delete(user)
    await session.commit()
    if user_query:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Пользователь удален успешно"}
