from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import RATING_IMPACT
from database.db import get_async_session
from database.models import User, Event, Rating
from keyboards.main_menu import get_rating_keyboard, get_stars_keyboard
from services.rating_service import rate_user, update_user_rating
from services.user_service import get_user_by_telegram_id
from utils.states import RatingState

router = Router()

# Обработка команды для оценки участников мероприятия
@router.message(Command("rate"))
async def cmd_rate(message: Message, state: FSMContext):
    """Обработчик команды /rate"""
    # Проверяем, зарегистрирован ли пользователь
    async for session in get_async_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer(
                "Для оценки участников необходимо сначала заполнить профиль. "
                "Используйте команду /profile для регистрации."
            )
            return
        
        # Получаем мероприятия, которые посетил пользователь и еще не оценил всех участников
        from services.event_service import get_events_to_rate
        events_to_rate = await get_events_to_rate(session, user.id)
        
        if not events_to_rate:
            await message.answer(
                "У вас нет мероприятий для оценки. "
                "Вы можете оценить участников только после посещения мероприятия."
            )
            return
        
        # Показываем список мероприятий для оценки
        await message.answer(
            "Выберите мероприятие, участников которого вы хотите оценить:",
            reply_markup=get_rating_keyboard(events_to_rate)
        )
        
        # Устанавливаем состояние выбора мероприятия для оценки
        await state.set_state(RatingState.selecting_event)

# Обработка выбора мероприятия для оценки
@router.callback_query(F.data.startswith("rate_event_"), RatingState.selecting_event)
async def select_event_to_rate(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора мероприятия для оценки"""
    event_id = int(callback.data.split("_")[2])
    
    # Сохраняем ID мероприятия в контексте
    await state.update_data(event_id=event_id)
    
    async for session in get_async_session():
        # Получаем мероприятие и его участников
        from services.event_service import get_event_by_id
        event = await get_event_by_id(session, event_id)
        
        if not event:
            await callback.message.answer("Мероприятие не найдено. Пожалуйста, попробуйте снова.")
            await callback.answer()
            await state.clear()
            return
        
        # Получаем пользователя
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        # Получаем список участников, которых еще не оценили
        from services.rating_service import get_users_to_rate
        users_to_rate = await get_users_to_rate(session, event_id, user.id)
        
        if not users_to_rate:
            await callback.message.answer(
                "Вы уже оценили всех участников этого мероприятия. "
                "Выберите другое мероприятие или вернитесь в главное меню."
            )
            await callback.answer()
            await state.clear()
            return
        
        # Выбираем первого пользователя для оценки
        user_to_rate = users_to_rate[0]
        
        # Сохраняем ID пользователя для оценки в контексте
        await state.update_data(user_to_rate_id=user_to_rate.id)
        
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            f"Оцените участника <b>{user_to_rate.display_name}</b> по шкале от 1 до 5 звезд:",
            parse_mode="HTML",
            reply_markup=get_stars_keyboard()
        )
        
        # Устанавливаем состояние выбора оценки
        await state.set_state(RatingState.selecting_rating)
        
        await callback.answer()

# Обработка выбора оценки
@router.callback_query(F.data.startswith("rate_"), RatingState.selecting_rating)
async def select_rating(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора оценки"""
    rating = int(callback.data.split("_")[1])
    
    # Получаем данные из контекста
    data = await state.get_data()
    event_id = data["event_id"]
    user_to_rate_id = data["user_to_rate_id"]
    
    async for session in get_async_session():
        # Получаем пользователя
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        # Сохраняем оценку в базе данных
        await rate_user(session, event_id, user.id, user_to_rate_id, rating)
        
        # Обновляем рейтинг пользователя
        await update_user_rating(session, user_to_rate_id, RATING_IMPACT[rating])
        
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(f"Спасибо за оценку! Вы поставили {rating} звезд.")
        
        # Проверяем, остались ли еще пользователи для оценки
        from services.rating_service import get_users_to_rate
        users_to_rate = await get_users_to_rate(session, event_id, user.id)
        
        if users_to_rate:
            # Выбираем следующего пользователя для оценки
            next_user_to_rate = users_to_rate[0]
            
            # Сохраняем ID следующего пользователя для оценки в контексте
            await state.update_data(user_to_rate_id=next_user_to_rate.id)
            
            await callback.message.answer(
                f"Оцените участника <b>{next_user_to_rate.display_name}</b> по шкале от 1 до 5 звезд:",
                parse_mode="HTML",
                reply_markup=get_stars_keyboard()
            )
        else:
            await callback.message.answer(
                "Вы оценили всех участников этого мероприятия. Спасибо за ваши оценки!"
            )
            await state.clear()
        
        await callback.answer()