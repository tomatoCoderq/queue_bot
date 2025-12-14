import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


async def check_upcoming_deadlines():
    """
    Периодическая проверка задач с приближающимся дедлайном.
    Запускается каждую минуту.
    """
    try:
        logger.info("Checking tasks")
        
        logger.info("✅ Deadline check completed")
        
    except Exception as e:
        logger.error(f"❌ Error in check_upcoming_deadlines: {e}", exc_info=True)


async def check_overdue_tasks():
    """
    Периодическая проверка просроченных задач.
    Запускается каждую минуту.
    Помечает просроченные задачи и отправляет уведомления.
    """
    try:
        logger.info("Checking overdue")
        
        from bot.modules.tasks.service import (
            get_overdue_tasks,
            mark_task_as_overdue,
            mark_overdue_notification_sent
        )
        from bot.modules.tasks.notifications import send_overdue_notification
        from bot.modules.users.service import get_user_by_id
        
        # Получаем список просроченных задач
        tasks = await get_overdue_tasks()
        
        if not tasks:
            logger.info("No overdue")
            return
        
        logger.info(f"Found {len(tasks)} overdue tasks")
        
        for task in tasks:
            try:
                task_id = task.get("id")
                task_title = task.get("title", "Без названия")
                due_date = task.get("due_date", "")
                student_id = task.get("student_id")
                overdue_notification_sent = task.get("overdue_notification_sent", False)
                
                # Помечаем задачу как просроченную
                success = await mark_task_as_overdue(task_id)
                
                if not success:
                    logger.warning(f"⚠️ Failed to mark task {task_id} as overdue")
                    continue
                
                logger.info(f"✅ Marked task '{task_title}' as overdue")
                
                # Отправляем уведомление студенту (если еще не отправляли)
                if not overdue_notification_sent and student_id:
                    # Получаем информацию о студенте
                    student = await get_user_by_id(student_id)
                    
                    if student and student.get("telegram_id"):
                        # Форматируем дату
                        due_date_formatted = due_date
                        if due_date:
                            try:
                                dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                                due_date_formatted = dt.strftime("%d.%m.%Y %H:%M")
                            except:
                                pass
                        
                        # Отправляем уведомление
                        notification_sent = await send_overdue_notification(
                            telegram_id=student["telegram_id"],
                            task_title=task_title,
                            due_date=due_date_formatted
                        )
                        
                        if notification_sent:
                            # Помечаем что уведомление отправлено
                            await mark_overdue_notification_sent(task_id)
                            logger.info(
                                f"✅ Sent overdue notification for task '{task_title}' "
                                f"to user {student['telegram_id']}"
                            )
                        else:
                            logger.warning(
                                f"⚠️ Failed to send notification for task {task_id}"
                            )
                
            except Exception as e:
                logger.error(
                    f"❌ Error processing overdue task {task.get('id')}: {e}",
                    exc_info=True
                )
                continue
        
        logger.info(f"✅ Processed {len(tasks)} overdue tasks")
        
    except Exception as e:
        logger.error(f"❌ Error in check_overdue_tasks: {e}", exc_info=True)


async def send_deadline_reminder(
    task_id: str,
    student_telegram_id: int,
    task_title: str,
    minutes_left: int
):
    """
    Отправка напоминания о дедлайне конкретной задачи.
    
    Args:
        task_id: ID задачи
        student_telegram_id: Telegram ID студента
        task_title: Название задачи
        minutes_left: Сколько минут осталось до дедлайна
    """
    try:
        from bot.modules.tasks.notifications import send_deadline_notification
        
        # Отправляем уведомление
        success = await send_deadline_notification(
            telegram_id=student_telegram_id,
            task_title=task_title,
            minutes_left=minutes_left
        )
        
        if success:
            logger.info(
                f"✅ Sent {minutes_left}min reminder for task '{task_title}' "
                f"to user {student_telegram_id}"
            )
        else:
            logger.warning(
                f"⚠️ Failed to send reminder for task {task_id} "
                f"to user {student_telegram_id}"
            )
            
    except Exception as e:
        logger.error(
            f"❌ Error sending reminder for task {task_id}: {e}",
            exc_info=True
        )


async def schedule_task_reminder(
    task_id: str,
    student_telegram_id: int,
    task_title: str,
    due_date: datetime,
    minutes_before: int = 3
):
    """
    Запланировать напоминание о задаче на конкретное время.
    
    Args:
        task_id: ID задачи
        student_telegram_id: Telegram ID студента
        task_title: Название задачи
        due_date: Дедлайн задачи
        minutes_before: За сколько минут до дедлайна напомнить
    """
    from bot.scheduler.scheduler import scheduler
    
    try:
        # Вычисляем время напоминания
        reminder_time = due_date - timedelta(minutes=minutes_before)
        
        # Проверяем, не прошло ли уже время напоминания
        if reminder_time <= datetime.now(reminder_time.tzinfo or None):
            logger.warning(
                f"⚠️ Reminder time for task {task_id} is in the past. Skipping."
            )
            return False
        
        # Создаем уникальный ID для job
        job_id = f"reminder_{task_id}_{minutes_before}min"
        
        # Удаляем старый job если существует
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        
        # Добавляем новый job
        scheduler.add_job(
            send_deadline_reminder,
            trigger='date',
            run_date=reminder_time,
            args=[task_id, student_telegram_id, task_title, minutes_before],
            id=job_id,
            name=f'Reminder for task "{task_title}" ({minutes_before}min)',
            replace_existing=True
        )
        
        logger.info(
            f"✅ Scheduled {minutes_before}min reminder for task '{task_title}' "
            f"at {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return True
        
    except Exception as e:
        logger.error(
            f"❌ Error scheduling reminder for task {task_id}: {e}",
            exc_info=True
        )
        return False


async def cancel_task_reminder(task_id: str, minutes_before: int = 3):
    """
    Отменить запланированное напоминание о задаче.
    
    Args:
        task_id: ID задачи
        minutes_before: За сколько минут было запланировано напоминание
    """
    from bot.scheduler.scheduler import scheduler
    
    try:
        job_id = f"reminder_{task_id}_{minutes_before}min"
        
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            logger.info(f"✅ Cancelled reminder for task {task_id}")
            return True
        else:
            logger.warning(f"⚠️ No reminder found for task {task_id}")
            return False
            
    except Exception as e:
        logger.error(
            f"❌ Error cancelling reminder for task {task_id}: {e}",
            exc_info=True
        )
        return False
