from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload

from src.api.schema import UserDataSchema
from src.core.db import SessionAnnotated
from src.core.paginator import Paginator
from src.models.model import UserData, InsuranceInfo

user_router = APIRouter()


@user_router.get("/health")
async def health_check():
    return {"status": "ok"}

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
    query = select(UserData).options(joinedload(UserData.insurance)).where(UserData.id == user_id)
    result = await session.execute(query)
    user = result.scalars().unique().first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user.to_dict(include_insurance=True)


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


@user_router.get("/users/get_all/")
async def get_all_users(
        session: SessionAnnotated,
        date_insurance_end: Optional[str] = Query(None),
        search_query: Optional[str] = Query(None),
        polis_type: Optional[str] = Query(None),
        page_number: int = Query(1, alias="page"),
        page_size: int = Query(10, alias="size")
):
    end_date = None
    if date_insurance_end:
        try:
            end_date = datetime.strptime(date_insurance_end, '%d.%m.%Y').date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_insurance_end format. Use DD.MM.YYYY")

    query = select(UserData).options(joinedload(UserData.insurance)).join(InsuranceInfo)
    if end_date:
        query = query.filter(InsuranceInfo.time_insure_end >= end_date)
    if polis_type:
        query = query.filter(InsuranceInfo.polis_type == polis_type)
    if search_query:
        search_pattern = f"%{search_query.capitalize()}%"
        query = query.filter(or_(
            UserData.first_name.like(search_pattern),
            UserData.last_name.like(search_pattern),
            UserData.middle_name.like(search_pattern),
        ))

    result = await session.execute(query)
    users = result.scalars().unique().all()

    paginator = Paginator(users, page_size)
    page = paginator.page(page_number)

    if not page.object_list:
        raise HTTPException(status_code=404, detail="Users not found")

    return {
        "total": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": page.number,
        "users": [user.to_dict(include_insurance=True) for user in page.object_list]
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
