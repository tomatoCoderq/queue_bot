from sqlmodel import select
from uuid import UUID

from src.storages.dependencies import DbSession
from src.storages import models
from src.modules.users.schemes import UpdateUserRequest


async def read_all_users(session: DbSession):  # type: ignore
    users = await session.execute(select(models.User))
    return users.scalars().all()


async def read_all_clients(session: DbSession):  # type: ignore
    statement = select(models.Client)
    result = await session.execute(statement)
    return result.scalars().all()


# async def read_all_students(session: DbSession):  # type: ignore
#     statement = select(BaseTelegramUser).where(
#         BaseTelegramUser.role == "STUDENT")
#     result = await session.execute(statement)
#     return result.scalars().all()


# async def read_all_teachers(session: DbSession):  # type: ignore
#     statement = select(BaseTelegramUser).where(
#         BaseTelegramUser.role == "TEACHER")
#     result = await session.execute(statement)
#     return result.scalars().all()


async def read_all_operators(session: DbSession):  # type: ignore
    statement = select(models.Operator)
    result = await session.execute(statement)
    return result.scalars().all()


async def add_user(user_create: models.User, session: DbSession):  # type: ignore
    session.add(user_create)
    await session.commit()
    await session.refresh(user_create)
    return user_create


async def add_client(user_create: models.User, session: DbSession):  # type: ignore
    session.add(user_create)
    await session.commit()
    await session.refresh(user_create)

    client = models.Client(user_id=user_create.id)
    session.add(client)
    await session.commit()
    await session.refresh(client)

    return client


async def add_client(user_create: models.User, session: DbSession):  # type: ignore
    response = {}

    session.add(user_create)
    await session.commit()
    await session.refresh(user_create)

    response['user'] = user_create.model_dump()

    client = models.Client(user_id=user_create.id)
    session.add(client)
    await session.commit()
    await session.refresh(client)

    response['client'] = client.model_dump()

    return response


async def add_operator(user_create: models.User, session: DbSession):  # type: ignore
    session.add(user_create)
    await session.commit()
    await session.refresh(user_create)

    operator = models.Operator(user_id=user_create.id)
    session.add(operator)
    await session.commit()
    await session.refresh(operator)

    return operator


async def read_user_by_id(user_id: UUID, session: DbSession):  # type: ignore
    statement = select(models.User).where(models.User.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    return user


# type: ignore
async def read_user_by_telegram_id(telegram_id: int, session: DbSession): # type: ignore
    statement = select(models.User).where(
        models.User.telegram_id == telegram_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    return user


async def read_client_by_user_id(user_id: UUID, session: DbSession):  # type: ignore
    stmt = (
        select(models.Client).where(models.Client.user_id == user_id)
    )
    res = await session.execute(stmt)
    client = res.scalar_one_or_none()
    return client


# type: ignore
async def read_client_by_telegram_id(telegram_id: int, session: DbSession): # type: ignore
    stmt = (
        select(models.Client).join(models.User,
                                   models.Client.user_id == models.User.id)  # type: ignore
        .where(models.User.telegram_id == telegram_id)
    )
    res = await session.execute(stmt)
    client = res.scalar_one_or_none()
    return client


async def delete_user_repo(user: models.User, session: DbSession):  # type: ignore
    await session.delete(user)
    await session.commit()


async def update_user_repo(user: models.User, user_update: UpdateUserRequest, session: DbSession):  # type: ignore
    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    await session.commit()
    await session.refresh(user)
    return user
