import logging
from html import escape
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

logger = logging.getLogger(__name__)


async def send_overdue_notification(
    telegram_id: int,
    task_title: str,
    due_date: str,
    bot: Bot = None
) -> bool:
    """Отправить уведомление студенту о просроченной задаче."""
    try:
        # Получаем бота из глобального контекста если не передан
        if bot is None:
            from bot.__main__ import bot as global_bot
            bot = global_bot
        
        message = (
            f"⚠️ <b>Задача просрочена!</b>\n\n"
            f"📌 Задача: <b>{escape(task_title)}</b>\n"
            f"⏰ Дедлайн был: {escape(due_date)}\n\n"
            f"🚨 Пожалуйста, завершите задачу как можно скорее!"
        )
        
        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode="HTML"
        )
        
        logger.info(
            f"✅ Sent overdue notification to user {telegram_id} "
            f"for task '{task_title}'"
        )
        return True
        
    except TelegramForbiddenError:
        logger.warning(
            f"⚠️ User {telegram_id} blocked the bot. Cannot send notification."
        )
        return False
        
    except TelegramBadRequest as e:
        logger.error(
            f"❌ Bad request sending notification to {telegram_id}: {e}"
        )
        return False
        
    except Exception as e:
        logger.error(
            f"❌ Error sending overdue notification to {telegram_id}: {e}",
            exc_info=True
        )
        return False


async def send_deadline_notification(
    telegram_id: int,
    task_title: str,
    minutes_left: int,
    bot: Bot = None
) -> bool:
    """
    Отправить уведомление о приближающемся дедлайне.
    
    Args:
        telegram_id: Telegram ID студента
        task_title: Название задачи
        minutes_left: Минут до дедлайна
        bot: Экземпляр бота
    
    Returns:
        bool: True если успешно
    """
    try:
        if bot is None:
            from bot.__main__ import bot as global_bot
            bot = global_bot
        
        emoji = "🔔"
        if minutes_left <= 3:
            emoji = "⚠️"
        elif minutes_left <= 10:
            emoji = "⏰"
        
        message = (
            f"{emoji} <b>Напоминание о дедлайне!</b>\n\n"
            f"📌 Задача: <b>{escape(task_title)}</b>\n"
            f"⏱ Осталось: <b>{minutes_left} мин</b>\n\n"
        )
        
        if minutes_left <= 3:
            message += "🚨 <b>Срочно! Время почти истекло!</b>"
        elif minutes_left <= 10:
            message += "⚡️ Поторопитесь, времени мало!"
        else:
            message += "💡 Не забудьте завершить задачу вовремя!"
        
        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode="HTML"
        )
        
        logger.info(
            f"✅ Sent deadline notification to user {telegram_id} "
            f"for task '{task_title}' ({minutes_left}min left)"
        )
        return True
        
    except Exception as e:
        logger.error(
            f"❌ Error sending deadline notification to {telegram_id}: {e}",
            exc_info=True
        )
        return False


async def send_task_approved_notification(
    telegram_id: int,
    task_title: str,
    bot: Bot = None
) -> bool:
    """Отправить уведомление об одобрении задачи"""
    try:
        if bot is None:
            from bot.__main__ import bot as global_bot
            bot = global_bot
        
        message = (
            f"✅ <b>Задача одобрена!</b>\n\n"
            f"📌 Задача: <b>{escape(task_title)}</b>\n\n"
            f"🎉 Поздравляем! Преподаватель одобрил вашу работу."
        )
        
        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode="HTML"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error sending approval notification: {e}")
        return False


async def send_task_rejected_notification(
    telegram_id: int,
    task_title: str,
    rejection_comment: str,
    new_deadline: str,
    bot: Bot = None
) -> bool:
    """Отправить уведомление об отклонении задачи"""
    try:
        if bot is None:
            from bot.__main__ import bot as global_bot
            bot = global_bot
        
        message = (
            f"❌ <b>Задача отклонена</b>\n\n"
            f"📌 Задача: <b>{escape(task_title)}</b>\n\n"
            f"💬 <b>Комментарий преподавателя:</b>\n{escape(rejection_comment)}\n\n"
            f"⏰ <b>Новый дедлайн:</b> {escape(new_deadline)}\n"
            f"(Продлен на 1 час)\n\n"
            f"📝 Пожалуйста, исправьте и отправьте работу снова."
        )
        
        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode="HTML"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error sending rejection notification: {e}")
        return False


async def send_task_submitted_notification(
    operator_telegram_id: int,
    student_name: str,
    task_title: str,
    bot: Bot = None
) -> bool:
    """Отправить уведомление преподавателю о новой задаче на проверке"""
    try:
        if bot is None:
            from bot.__main__ import bot as global_bot
            bot = global_bot
        
        message = (
            f"📝 <b>Новая задача на проверке</b>\n\n"
            f"👤 Студент: <b>{escape(student_name)}</b>\n"
            f"📌 Задача: <b>{escape(task_title)}</b>\n\n"
            f"Студент отправил работу на проверку."
        )
        
        await bot.send_message(
            chat_id=operator_telegram_id,
            text=message,
            parse_mode="HTML"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error sending submission notification: {e}")
        return False
