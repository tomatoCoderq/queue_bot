from sqlmodel import select
from typing import List, Optional
from uuid import UUID

from src.storages.dependencies import DbSession
from src.storages.models import StoredFiles


async def save_file(file_data: StoredFiles, db: DbSession) -> StoredFiles: # type: ignore
    """Сохранение файла в базу данных"""
    db.add(file_data)
    await db.commit()
    await db.refresh(file_data)
    return file_data


async def get_files_by_task(task_id: UUID, db: DbSession) -> List[StoredFiles]: # type: ignore
    """Получение всех файлов задачи"""
    result = await db.execute(
        select(StoredFiles).where(StoredFiles.task_id == task_id)
    )
    return result.scalars().all()


async def get_file_by_id(file_id: UUID, db: DbSession) -> Optional[StoredFiles]: # type: ignore
    """Получение файла по ID"""
    result = await db.execute(
        select(StoredFiles).where(StoredFiles.id == file_id)
    )
    return result.scalar()


async def delete_file_record(file_id: UUID, db: DbSession) -> bool: # type: ignore
    """Удаление записи файла из базы данных"""
    file_obj = await get_file_by_id(file_id, db)
    if not file_obj:
        return False
    
    await db.delete(file_obj)
    await db.commit()
    return True