from typing import List
from sqlmodel import select
from uuid import UUID

from src.storages.dependencies import DbSession
from src.storages.models import *
from src.modules.users.schemes import UpdateUserRequest
from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession


async def read_all_users(session: DbSession):  # type: ignore
    users = await session.execute(select(BaseTelegramUser))
    return users.scalars().all()


async def read_all_clients(session: DbSession):  # type: ignore
    statement = select(BaseTelegramUser).where(
        BaseTelegramUser.role == "CLIENT")
    result = await session.execute(statement)
    return result.scalars().all()


async def read_all_students(session: DbSession):  # type: ignore
    statement = select(BaseTelegramUser).where(
        BaseTelegramUser.role == "STUDENT")
    result = await session.execute(statement)
    return result.scalars().all()


async def read_all_teachers(session: DbSession):  # type: ignore
    statement = select(BaseTelegramUser).where(
        BaseTelegramUser.role == "TEACHER")
    result = await session.execute(statement)
    return result.scalars().all()


async def read_all_operators(session: DbSession):  # type: ignore
    statement = select(BaseTelegramUser).where(
        BaseTelegramUser.role == "OPERATOR")
    result = await session.execute(statement)
    return result.scalars().all()


async def add_user(user_create: BaseTelegramUser, session: DbSession):  # type: ignore
    session.add(user_create)
    await session.commit()
    await session.refresh(user_create)
    return user_create


async def add_client(user_create: BaseTelegramUser, session: DbSession):  # type: ignore
    session.add(user_create)
    await session.commit()
    await session.refresh(user_create)

    client = Client(user_id=user_create.id)
    session.add(client)
    await session.commit()
    await session.refresh(client)

    return client


async def add_student(user_create: BaseTelegramUser, session: DbSession):  # type: ignore
    print("Starting to create user:", user_create)
    print(">>> add_student called")
    print("session type:", type(session))
    print("is AsyncSession:", isinstance(session, AsyncSession))
    
    response = {}
    
    session.add(user_create)
    await session.commit()
    await session.refresh(user_create)
    # print("Created user:", user_create)
    response['user'] = user_create.model_dump()

    print("Starting to create client for user_id:", user_create.id)
    client = Client(user_id=user_create.id)
    session.add(client)
    await session.commit()
    await session.refresh(client)
    # print("Created client:", client)
    response['client'] = client.model_dump()

    print("Starting to create student for client_id:", client.id)
    student = Student(client_id=client.id)
    session.add(student)
    await session.commit()
    await session.refresh(student)
    print("Created student:", student)
    response['student'] = student

    return response


async def add_operator(user_create: BaseTelegramUser, session: DbSession):  # type: ignore
    session.add(user_create)
    await session.commit()
    await session.refresh(user_create)

    operator = Operator(user_id=user_create.id, type="admin")
    session.add(operator)
    await session.commit()
    await session.refresh(operator)

    return operator


async def read_user_by_id(user_id: UUID, session: DbSession):  # type: ignore
    print("Reading user by ID:", user_id)
    statement = select(BaseTelegramUser).where(BaseTelegramUser.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    print("Fetched user:", user)
    return user

async def read_student_by_user_id(user_id: UUID, session: DbSession):  # type: ignore
    stmt = (
        select(Student)
        .join(Client, Student.client_id == Client.id) # type: ignore
        .join(BaseTelegramUser, Client.user_id == BaseTelegramUser.id) # type: ignore
        .where(BaseTelegramUser.id == user_id)
        .options(
            selectinload(Student.client),   # на случай, если нужен client # type: ignore
            # заранее подгрузим tasks, если планируем читать/модифицировать
            selectinload(Student.tasks) # type: ignore
        )
    )
    res = await session.execute(stmt)
    student = res.scalar_one_or_none()
    print("Fetched student:", student)
    return student


# type: ignore
async def read_user_by_telegram_id(telegram_id: int, session: DbSession): # type: ignore
    statement = select(BaseTelegramUser).where(
        BaseTelegramUser.telegram_id == telegram_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    return user


async def get_student_by_user_id(user_id: UUID, session: DbSession):  # type: ignore
    stmt = (
        select(Student)
        .join(Client, Student.client_id == Client.id) # type: ignore
        .join(BaseTelegramUser, Client.user_id == BaseTelegramUser.id) # type: ignore
        .where(BaseTelegramUser.id == user_id)
        .options(
            selectinload(Student.client),   # на случай, если нужен client # type: ignore
            # заранее подгрузим tasks, если планируем читать/модифицировать
            selectinload(Student.tasks) # type: ignore
        )
    )
    res = await session.execute(stmt)
    student = res.scalar_one_or_none()
    print("Fetched student:", student)

    res = await session.execute(select(Client).where(Client.user_id == user_id))
    client = res.scalar_one_or_none()
    print("client:", client)
    return student


async def delete_user_repo(user: BaseTelegramUser, session: DbSession):  # type: ignore
    await session.delete(user)
    await session.commit()


async def update_user_repo(user: BaseTelegramUser, user_update: UpdateUserRequest, session: DbSession):  # type: ignore
    for key, value in user_update.model_dump(exclude_unset=True).items():

        setattr(user, key, value)

    await session.commit()
    await session.refresh(user)
    return user
