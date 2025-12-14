from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List, Optional
from uuid import UUID
import os
import aiofiles
from pathlib import Path

from src.storages.dependencies import DbSession
from src.modules.files import repository as repo
from src.modules.files.schemes import *
from src.storages.models import StoredFiles
from src.errors import NotFoundError
from loguru import logger

router = APIRouter(prefix="/files", tags=["files"])

# Директория для хранения файлов
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/",
             response_model=FileUploadResponse,
             status_code=201,
             description="Upload file")
async def upload_file(
    db: DbSession,  # type: ignore
    file: UploadFile = File(...),
    file_id: Optional[str] = Form(None),
    task_id: Optional[str] = Form(None),
    type: Optional[str] = Form(None), 
):
    """Загрузка файла на сервер"""
    logger.info(f"Uploading file: {file.filename}")
    try:
        import time
        timestamp = str(int(time.time()))
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename

        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        stored_file = StoredFiles(
            filename=file.filename,
            type=type,
            file_id=file_id if file_id else "",
            task_id=UUID(task_id) if task_id else None,
            path=str(file_path),
        )

        saved_file = await repo.save_file(stored_file, db)
        return saved_file

    except OSError as e:
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        logger.error(f"File write error: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка записи файла: {e}")


@router.get("/task/{task_id}",
            response_model=List[FileReadResponse],
            description="Get files by task ID")
async def get_task_files(task_id: UUID, db: DbSession):  # type: ignore
    """Получение файлов задачи"""
    logger.info(f"Fetching files for task: {task_id}")
    files = await repo.get_files_by_task(task_id, db)
    return files


@router.delete("/{file_id}",
               status_code=204,
               description="Delete file")
async def delete_file(file_id: UUID, db: DbSession):  # type: ignore
    """Удаление файла"""
    logger.info(f"Deleting file: {file_id}")
    file_obj = await repo.get_file_by_id(file_id, db)
    if not file_obj:
        logger.warning(f"File not found: {file_id}")
        raise NotFoundError("file")

    success = await repo.delete_file_record(file_id, db)
    if not success:
        logger.error(f"Failed to delete file from database: {file_id}")
        raise HTTPException(status_code=404, detail="Не удалось удалить файл из базы")

    try:
        if os.path.exists(file_obj.file_path):
            os.unlink(file_obj.file_path)
    except OSError as e:
        logger.error(f"Failed to delete file from disk: {e}")
        raise HTTPException(status_code=500, detail=f"Не удалось удалить файл с диска: {e}")

    return {"message": "File deleted successfully"}


@router.get("/{file_id}/download",
            description="Download file")
async def download_file(file_id: UUID, db: DbSession):  # type: ignore
    """Скачивание файла"""
    logger.info(f"Downloading file: {file_id}")
    file_obj = await repo.get_file_by_id(file_id, db)
    if not file_obj:
        logger.warning(f"File not found: {file_id}")
        raise NotFoundError("file")

    if not os.path.exists(file_obj.file_path):
        logger.warning(f"File not found on disk: {file_obj.file_path}")
        raise HTTPException(status_code=404, detail="Файл не найден на диске")

    return FileResponse(
        path=file_obj.file_path,
        filename=file_obj.filename,
        media_type='application/octet-stream'
    )
