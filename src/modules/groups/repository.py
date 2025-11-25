
from sqlmodel import select

from src.storages.models import Task
from src.modules.tasks.schemes import *
from src.storages.dependencies import DbSession
from src.storages.models import *
from src.storages import models


async def add_new_group(group: Group, db: DbSession):  # type: ignore
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


async def read_all_groups(db: DbSession):  # type: ignore
    result = await db.execute(select(Group))
    return result.scalars().all()


async def read_group(group_id: UUID, db: DbSession):  # type: ignore
    result = await db.execute(select(Group).where(Group.id == group_id))
    return result.scalar()

async def read_group_by_name(name: str, db: DbSession): # type: ignore
    result = await db.execute(select(Group).where(Group.name == name))
    return result.scalar()


# async def add_student_to_group(group: Group, student: Student, db: DbSession):  # type: ignore
#     print(group)
#     group.students.append(student)
#     await db.commit()
#     await db.refresh(group)
#     return group


async def add_client_to_group(group: Group, user: models.User, db: DbSession):  # type: ignore

    result = await db.execute(
        select(models.Client)
        .where(models.Client.user_id == user.id)
    )
    client = result.scalar()
    
    if not client:
        raise ValueError(f"Client not found for user {user.id}")
    
    # Устанавливаем group_id у клиента
    client.group_id = group.id
    
    # Добавляем изменения в сессию
    db.add(client)
    
    # Коммитим изменения
    await db.commit()
    
    # Обновляем объекты из БД
    await db.refresh(client)
    await db.refresh(group)
    
    return group


async def remove_client(group: Group, client: Client, db: DbSession):  # type: ignore
    group.clients.remove(client)
    await db.commit()
    await db.refresh(group)
    return group


async def get_tasks(group: Group, db: DbSession):  # type: ignore
    result = await db.execute(select(Task).where(Task.group == group))
    return result.scalars().all()
