from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_async_session
from services.user_service import get_user_by_telegram_id

class AuthMiddleware(BaseMiddleware):
    """
    Middleware для проверки аутентификации пользователя.
    Добавляет объект пользователя из БД в данные хэндлера, если пользователь зарегистрирован.
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем ID пользователя из события
        user_id = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id:
            # Получаем сессию БД
            async for session in get_async_session():
                # Получаем пользователя из БД
                user = await get_user_by_telegram_id(session, user_id)
                
                # Добавляем пользователя в данные хэндлера
                data["db_user"] = user
        
        return await handler(event, data)