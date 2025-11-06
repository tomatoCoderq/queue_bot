import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

# Конфигурация планировщика
jobstores = {
    'default': MemoryJobStore()
}

executors = {
    'default': AsyncIOExecutor()
}

job_defaults = {
    'coalesce': True,  # Объединять пропущенные задачи
    'max_instances': 3,  # Максимум 3 экземпляра одной задачи
    'misfire_grace_time': 60  # Допустимое опоздание в секундах
}

# Создаем планировщик
scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone=pytz.UTC  # Используем UTC
)


async def setup_scheduler():
    """Запуск планировщика"""
    if not scheduler.running:
        scheduler.start()
        logger.info("✅ APScheduler started")
        
        # Добавляем периодическую проверку дедлайнов (каждую минуту)
        from bot.scheduler.jobs import check_upcoming_deadlines
        
        scheduler.add_job(
            check_upcoming_deadlines,
            trigger='interval',
            minutes=1,
            id='check_deadlines',
            replace_existing=True,
            name='Check upcoming task deadlines'
        )
        logger.info("✅ Periodic deadline check job added")
        
        # Добавляем периодическую проверку просроченных задач (каждую минуту)
        from bot.scheduler.jobs import check_overdue_tasks
        
        scheduler.add_job(
            check_overdue_tasks,
            trigger='interval',
            seconds=10,
            id='check_overdue',
            replace_existing=True,
            name='Check and mark overdue tasks'
        )
        logger.info("✅ Periodic overdue check job added")


async def shutdown_scheduler():
    """Остановка планировщика"""
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("✅ APScheduler stopped")
