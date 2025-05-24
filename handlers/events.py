from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import POPULAR_CITIES
from database.db import get_async_session
from database.models import User, Event, EventPurpose, EventTargetAudience, Gender
from keyboards.event_creation import (
    get_event_creation_rules_keyboard,
    get_event_purpose_keyboard,
    get_event_target_audience_keyboard,
    get_event_age_keyboard,
    get_confirmation_keyboard
)
from keyboards.main_menu import get_main_menu_keyboard, get_city_keyboard
from services.event_service import create_event, get_events_by_city, register_for_event, unregister_from_event
from services.user_service import get_user_by_telegram_id
from utils.states import EventCreationState, EventViewState

router = Router()

# Обработка команды /create - начало создания мероприятия
@router.message(Command("create"))
async def cmd_create_event(message: Message, state: FSMContext):
    """Обработчик команды /create"""
    # Проверяем, зарегистрирован ли пользователь
    async for session in get_async_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer(
                "Для создания мероприятия необходимо сначала заполнить профиль. "
                "Используйте команду /profile для регистрации."
            )
            return
        
        # Проверяем рейтинг пользователя
        if not user.can_create_events():
            await message.answer(
                "К сожалению, ваш рейтинг слишком низок для создания мероприятий. "
                "Минимальный требуемый рейтинг: 20, ваш текущий рейтинг: {user.rating}."
            )
            return
    
    # Начинаем процесс создания мероприятия
    await message.answer(
        "Для создания мероприятия вы должны ознакомиться с правилами публикации "
        "мероприятий и общения на площадке.",
        reply_markup=get_event_creation_rules_keyboard()
    )
    
    # Устанавливаем состояние для начала создания мероприятия
    await state.set_state(EventCreationState.waiting_for_rules_agreement)

# Обработка нажатия на кнопку "Ознакомиться" с правилами
@router.callback_query(F.data == "view_rules", EventCreationState.waiting_for_rules_agreement)
async def process_view_rules(callback: CallbackQuery):
    """Обработчик просмотра правил создания мероприятий"""
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "<b>Правила создания мероприятий</b>\n\n"
        "<b>1. Общие положения</b>\n\n"
        "• Мероприятия должны быть направлены на <b>общение, совместный досуг и позитивное взаимодействие</b>.\n"
        "• <b>Запрещено</b> создавать события с коммерческой выгодой (продажи, реклама услуг), "
        "а также мероприятия, нарушающие законы РФ.\n"
        "• Все участники должны чувствовать себя <b>комфортно и безопасно</b>.\n\n"
        "<b>2. Ограничения по содержанию</b>\n\n"
        "❌ <b>Нельзя</b>:\n"
        "• Употреблять ненормативную лексику в описании.\n"
        "• Указывать контакты (телефоны, соцсети) до подтверждения участия.\n"
        "• Размещать мероприятия с <b>политической, религиозной</b> или <b>экстремистской</b> повесткой.\n"
        "• Публиковать контент <b>18+</b> или провокационного характера.\n\n"
        "✅ <b>Можно</b>:\n"
        "• Организовывать <b>спортивные, творческие, развлекательные</b> и другие <b>дружеские</b> встречи.\n"
        "• Указывать <b>место, время, возрастные ограничения</b> и другую полезную информацию.\n"
        "• Просить участников взять с собой что-то необходимое (еду, инвентарь).\n\n"
        "<b>3. Ответственность организатора</b>\n\n"
        "• Вы <b>обязуетесь</b> быть на мероприятии в указанное время.\n"
        "• Если мероприятие <b>отменяется</b>, необходимо уведомить участников <b>минимум за 6 часов</b>.\n"
        "• Несоблюдение правил ведет к <b>снижению рейтинга</b> или <b>блокировке</b>.",
        parse_mode="HTML",
        reply_markup=get_confirmation_keyboard("rules")
    )
    await callback.answer()

# Обработка согласия с правилами
@router.callback_query(F.data == "agree_rules", EventCreationState.waiting_for_rules_agreement)
async def process_agree_rules(callback: CallbackQuery, state: FSMContext):
    """Обработчик согласия с правилами"""
    await callback.message.edit_reply_markup(reply_markup=None)
    
    # Получаем информацию о пользователе
    async for session in get_async_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        # Сохраняем город пользователя как значение по умолчанию
        await state.update_data(city=user.city)
    
    # Предлагаем выбрать город из списка или оставить текущий
    await callback.message.answer(
        f"Шаг 1 из 5: Выберите город проведения мероприятия.\n"
        f"По умолчанию будет использован ваш город: {user.city}",
        reply_markup=get_city_keyboard(POPULAR_CITIES, include_current=True, current_city=user.city)
    )
    
    # Переходим к следующему шагу - выбор города
    await state.set_state(EventCreationState.waiting_for_city)
    await callback.answer()

# Обработка выбора города для мероприятия
@router.callback_query(F.data.startswith("city_"), EventCreationState.waiting_for_city)
async def process_event_city_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора города для мероприятия"""
    city = callback.data.split("_")[1]
    
    # Сохраняем город в контексте
    await state.update_data(city=city)
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Шаг 2 из 5: Выберите цель мероприятия:",
        reply_markup=get_event_purpose_keyboard()
    )
    
    # Переходим к следующему шагу - выбор цели мероприятия
    await state.set_state(EventCreationState.waiting_for_purpose)
    await callback.answer()

# Обработка выбора цели мероприятия
@router.callback_query(F.data.startswith("purpose_"), EventCreationState.waiting_for_purpose)
async def process_event_purpose_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора цели мероприятия"""
    purpose_map = {
        "walk": EventPurpose.WALK,
        "meet": EventPurpose.MEET,
        "travel": EventPurpose.TRAVEL,
        "help": EventPurpose.HELP,
        "party": EventPurpose.PARTY
    }
    
    purpose_code = callback.data.split("_")[1]
    purpose = purpose_map.get(purpose_code)
    
    if not purpose:
        await callback.message.answer("Произошла ошибка. Выберите цель мероприятия еще раз.")
        await callback.answer()
        return
    
    # Сохраняем цель в контексте
    await state.update_data(purpose=purpose)
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Шаг 3 из 5: Для кого предназначено мероприятие?",
        reply_markup=get_event_target_audience_keyboard()
    )
    
    # Переходим к следующему шагу - выбор целевой аудитории
    await state.set_state(EventCreationState.waiting_for_target_audience)
    await callback.answer()

# Обработка выбора целевой аудитории
@router.callback_query(F.data.startswith("audience_"), EventCreationState.waiting_for_target_audience)
async def process_target_audience_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора целевой аудитории"""
    audience_map = {
        "male": EventTargetAudience.MALE,
        "female": EventTargetAudience.FEMALE,
        "all": EventTargetAudience.ALL
    }
    
    audience_code = callback.data.split("_")[1]
    target_audience = audience_map.get(audience_code)
    
    if not target_audience:
        await callback.message.answer("Произошла ошибка. Выберите целевую аудиторию еще раз.")
        await callback.answer()
        return
    
    # Сохраняем целевую аудиторию в контексте
    await state.update_data(target_audience=target_audience)
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Шаг 4 из 5: Укажите возрастные ограничения для участников",
        reply_markup=get_event_age_keyboard()
    )
    
    # Переходим к следующему шагу - выбор возрастных ограничений
    await state.set_state(EventCreationState.waiting_for_age_limits)
    await callback.answer()

# Обработка выбора "Указать возраст"
@router.callback_query(F.data == "specify_age", EventCreationState.waiting_for_age_limits)
async def process_specify_age(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора указания возрастных ограничений"""
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Введите минимальный возраст участников (число):"
    )
    
    # Переходим к состоянию ввода минимального возраста
    await state.set_state(EventCreationState.entering_min_age)
    await callback.answer()

# Обработка выбора "Без ограничений"
@router.callback_query(F.data == "no_age_limits", EventCreationState.waiting_for_age_limits)
async def process_no_age_limits(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора отсутствия возрастных ограничений"""
    # Сохраняем отсутствие возрастных ограничений
    await state.update_data(min_age=None, max_age=None)
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Шаг 5 из 5: Введите название и подробное описание мероприятия.\n"
        "Укажите где и когда оно состоится, что нужно взять с собой и другую важную информацию.\n\n"
        "Сначала введите название мероприятия:"
    )
    
    # Переходим к состоянию ввода названия мероприятия
    await state.set_state(EventCreationState.entering_title)
    await callback.answer()

# Обработка ввода минимального возраста
@router.message(EventCreationState.entering_min_age)
async def process_min_age_input(message: Message, state: FSMContext):
    """Обработчик ввода минимального возраста"""
    try:
        min_age = int(message.text.strip())
        
        # Проверка на корректность возраста
        if min_age < 14 or min_age > 100:
            await message.answer("Пожалуйста, введите корректный возраст (от 14 до 100 лет):")
            return
        
        # Сохраняем минимальный возраст в контексте
        await state.update_data(min_age=min_age)
        
        await message.answer("Теперь введите максимальный возраст участников (число):")
        
        # Переходим к состоянию ввода максимального возраста
        await state.set_state(EventCreationState.entering_max_age)
        
    except ValueError:
        await message.answer("Пожалуйста, введите корректный возраст (число):")

# Обработка ввода максимального возраста
@router.message(EventCreationState.entering_max_age)
async def process_max_age_input(message: Message, state: FSMContext):
    """Обработчик ввода максимального возраста"""
    try:
        max_age = int(message.text.strip())
        
        # Получаем данные из контекста
        data = await state.get_data()
        min_age = data.get("min_age", 14)
        
        # Проверка на корректность возраста
        if max_age < min_age or max_age > 100:
            await message.answer(f"Пожалуйста, введите корректный возраст (от {min_age} до 100 лет):")
            return
        
        # Сохраняем максимальный возраст в контексте
        await state.update_data(max_age=max_age)
        
        await message.answer(
            "Шаг 5 из 5: Введите название и подробное описание мероприятия.\n"
            "Укажите где и когда оно состоится, что нужно взять с собой и другую важную информацию.\n\n"
            "Сначала введите название мероприятия:"
        )
        
        # Переходим к состоянию ввода названия мероприятия
        await state.set_state(EventCreationState.entering_title)
        
    except ValueError:
        await message.answer("Пожалуйста, введите корректный возраст (число):")

# Обработка ввода названия мероприятия
@router.message(EventCreationState.entering_title)
async def process_title_input(message: Message, state: FSMContext):
    """Обработчик ввода названия мероприятия"""
    title = message.text.strip()
    
    # Проверка на корректность названия
    if len(title) < 5:
        await message.answer("Название мероприятия слишком короткое. Пожалуйста, введите более подробное название:")
        return
    
    # Сохраняем название в контексте
    await state.update_data(title=title)
    
    await message.answer(
        "Теперь введите подробное описание мероприятия.\n"
        "Укажите:\n"
        "- Дату и время проведения (в формате ДД.ММ.ГГГГ ЧЧ:ММ)\n"
        "- Место встречи\n"
        "- Что нужно взять с собой\n"
        "- Максимальное количество участников (если есть ограничение)\n"
        "- Любую другую важную информацию"
    )
    
    # Переходим к состоянию ввода описания
    await state.set_state(EventCreationState.entering_description)

# Обработка ввода описания мероприятия
@router.message(EventCreationState.entering_description)
async def process_description_input(message: Message, state: FSMContext):
    """Обработчик ввода описания мероприятия"""
    description = message.text.strip()
    
    # Проверка на корректность описания
    if len(description) < 20:
        await message.answer(
            "Описание мероприятия слишком короткое. Пожалуйста, предоставьте более подробную информацию:"
        )
        return
    
    # Сохраняем описание в контексте
    await state.update_data(description=description)
    
    # Просим указать дату и время мероприятия
    await message.answer(
        "Укажите дату и время мероприятия в формате ДД.ММ.ГГГГ ЧЧ:ММ, например: 15.06.2025 18:00"
    )
    
    # Переходим к состоянию ввода даты и времени
    await state.set_state(EventCreationState.entering_datetime)

# Обработка ввода даты и времени мероприятия
@router.message(EventCreationState.entering_datetime)
async def process_datetime_input(message: Message, state: FSMContext):
    """Обработчик ввода даты и времени мероприятия"""
    try:
        # Пытаемся распарсить дату и время
        event_datetime = datetime.strptime(message.text.strip(), "%d.%m.%Y %H:%M")
        
        # Проверяем, что дата не в прошлом
        if event_datetime < datetime.now():
            await message.answer(
                "Нельзя создать мероприятие в прошлом. Пожалуйста, укажите дату и время в будущем:"
            )
            return
        
        # Сохраняем дату и время в контексте
        await state.update_data(event_datetime=event_datetime)
        
        await message.answer(
            "Укажите максимальное количество участников (число). Если ограничения нет, введите 0:"
        )
        
        # Переходим к состоянию ввода максимального количества участников
        await state.set_state(EventCreationState.entering_max_participants)
        
    except ValueError:
        await message.answer(
            "Неверный формат даты и времени. Пожалуйста, укажите в формате ДД.ММ.ГГГГ ЧЧ:ММ, например: 15.06.2025 18:00"
        )

# Обработка ввода максимального количества участников
@router.message(EventCreationState.entering_max_participants)
async def process_max_participants_input(message: Message, state: FSMContext):
    """Обработчик ввода максимального количества участников"""
    try:
        max_participants = int(message.text.strip())
        
        # Если указан 0, то ограничения нет
        if max_participants == 0:
            max_participants = None
        elif max_participants < 2:
            await message.answer(
                "Минимальное количество участников должно быть не менее 2. Укажите корректное число:"
            )
            return
        
        # Сохраняем максимальное количество участников в контексте
        await state.update_data(max_participants=max_participants)
        
        # Получаем все собранные данные
        event_data = await state.get_data()
        
        # Формируем превью мероприятия для подтверждения
        purpose_names = {
            EventPurpose.WALK: "Пошли гулять",
            EventPurpose.MEET: "Давайте знакомиться",
            EventPurpose.TRAVEL: "Совместные поездки/путешествия",
            EventPurpose.HELP: "Друзья мне нужна помощь",
            EventPurpose.PARTY: "Пойдем тусить"
        }
        
        audience_names = {
            EventTargetAudience.MALE: "Только для мужчин",
            EventTargetAudience.FEMALE: "Только для женщин",
            EventTargetAudience.ALL: "Для всех"
        }
        
        age_limits = "Без ограничений"
        if event_data.get("min_age") and event_data.get("max_age"):
            age_limits = f"От {event_data['min_age']} до {event_data['max_age']} лет"
        
        max_participants_str = "Без ограничений"
        if event_data.get("max_participants"):
            max_participants_str = str(event_data["max_participants"])
        
        preview = (
            f"<b>{event_data['title']}</b>\n\n"
            f"<b>Город:</b> {event_data['city']}\n"
            f"<b>Цель:</b> {purpose_names[event_data['purpose']]}\n"
            f"<b>Для кого:</b> {audience_names[event_data['target_audience']]}\n"
            f"<b>Возраст участников:</b> {age_limits}\n"
            f"<b>Дата и время:</b> {event_data['event_datetime'].strftime('%d.%m.%Y %H:%M')}\n"
            f"<b>Максимальное количество участников:</b> {max_participants_str}\n\n"
            f"<b>Описание:</b>\n{event_data['description']}\n\n"
            f"Всё верно? Подтвердите создание мероприятия:"
        )
        
        await message.answer(preview, parse_mode="HTML", reply_markup=get_confirmation_keyboard("event"))
        
        # Переходим к состоянию подтверждения создания мероприятия
        await state.set_state(EventCreationState.confirming_event)
        
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число:")

# Обработка подтверждения создания мероприятия
@router.callback_query(F.data == "confirm_event", EventCreationState.confirming_event)
async def confirm_event_creation(callback: CallbackQuery, state: FSMContext):
    """Обработчик подтверждения создания мероприятия"""
    # Получаем все собранные данные
    event_data = await state.get_data()
    
    # Получаем информацию о пользователе
    async for session in get_async_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")
            await callback.answer()
            return
        
        # Создаем мероприятие в базе данных
        event = await create_event(
            session,
            creator_id=user.id,
            title=event_data["title"],
            city=event_data["city"],
            purpose=event_data["purpose"],
            target_audience=event_data["target_audience"],
            min_age=event_data.get("min_age"),
            max_age=event_data.get("max_age"),
            description=event_data["description"],
            event_date=event_data["event_datetime"],
            max_participants=event_data.get("max_participants")
        )
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Отлично! Ваше мероприятие успешно создано и доступно для других пользователей.\n"
        "Вы можете просматривать и управлять своими мероприятиями в профиле."
    )
    await callback.answer()
    
    # Сбрасываем состояние
    await state.clear()

# Обработка команды /events - просмотр мероприятий
@router.message(Command("events"))
async def cmd_events(message: Message, state: FSMContext):
    """Обработчик команды /events"""
    # Проверяем, зарегистрирован ли пользователь
    async for session in get_async_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer(
                "Для просмотра мероприятий необходимо сначала заполнить профиль. "
                "Используйте команду /profile для регистрации."
            )
            return
        
        # Проверяем рейтинг пользователя
        if not user.can_view_events():
            await message.answer(
                "К сожалению, ваш рейтинг слишком низок для просмотра мероприятий. "
                f"Минимальный требуемый рейтинг: 0, ваш текущий рейтинг: {user.rating}."
            )
            return
        
        # Сохраняем город пользователя в контексте для дальнейшего использования
        await state.update_data(city=user.city)
        
        await message.answer(
            f"Выберите город для просмотра мероприятий.\n"
            f"По умолчанию будут показаны мероприятия в вашем городе: {user.city}",
            reply_markup=get_city_keyboard(POPULAR_CITIES, include_current=True, current_city=user.city)
        )
        
        # Устанавливаем состояние для выбора города
        await state.set_state(EventViewState.selecting_city)

# Обработка выбора города для просмотра мероприятий
@router.callback_query(F.data.startswith("city_"), EventViewState.selecting_city)
async def process_view_city_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора города для просмотра мероприятий"""
    city = callback.data.split("_")[1]
    
    # Сохраняем выбранный город в контексте
    await state.update_data(selected_city=city)
    
    # Получаем мероприятия в выбранном городе
    async for session in get_async_session():
        events = await get_events_by_city(session, city)
        
        if not events:
            await callback.message.edit_reply_markup(reply_markup=None)
            await callback.message.answer(
                f"В городе {city} пока нет активных мероприятий. "
                f"Вы можете создать первое мероприятие с помощью команды /create!"
            )
            await callback.answer()
            await state.clear()
            return
        
        # Показываем найденные мероприятия
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(f"Найдено {len(events)} мероприятий в городе {city}:")
        
        # Отправляем информацию о каждом мероприятии
        for event in events:
            # Формируем информацию о мероприятии
            purpose_names = {
                EventPurpose.WALK: "Пошли гулять",
                EventPurpose.MEET: "Давайте знакомиться",
                EventPurpose.TRAVEL: "Совместные поездки/путешествия",
                EventPurpose.HELP: "Друзья мне нужна помощь",
                EventPurpose.PARTY: "Пойдем тусить"
            }
            
            audience_names = {
                EventTargetAudience.MALE: "Только для мужчин",
                EventTargetAudience.FEMALE: "Только для женщин",
                EventTargetAudience.ALL: "Для всех"
            }
            
            age_limits = "Без ограничений"
            if event.min_age and event.max_age:
                age_limits = f"От {event.min_age} до {event.max_age} лет"
            
            participants_count = len(event.participants)
            max_participants_str = f"{participants_count}/{event.max_participants}" if event.max_participants else f"{participants_count}"
            
            event_info = (
                f"<b>{event.title}</b>\n\n"
                f"<b>Организатор:</b> {event.creator.display_name}\n"
                f"<b>Цель:</b> {purpose_names[event.purpose]}\n"
                f"<b>Для кого:</b> {audience_names[event.target_audience]}\n"
                f"<b>Возраст участников:</b> {age_limits}\n"
                f"<b>Дата и время:</b> {event.event_date.strftime('%d.%m.%Y %H:%M')}\n"
                f"<b>Участники:</b> {max_participants_str}\n\n"
                f"<b>Описание:</b>\n{event.description}"
            )
            
            # Проверяем, может ли пользователь зарегистрироваться на мероприятие
            user = await get_user_by_telegram_id(session, callback.from_user.id)
            can_register = event.can_register(user)
            
            # Создаем клавиатуру с кнопкой регистрации, если пользователь может зарегистрироваться
            from keyboards.event_creation import get_event_registration_keyboard
            keyboard = get_event_registration_keyboard(event.id, can_register)
            
            await callback.message.answer(event_info, parse_mode="HTML", reply_markup=keyboard)
        
        await callback.answer()
        await state.clear()

# Обработка регистрации на мероприятие
@router.callback_query(F.data.startswith("register_"))
async def register_for_event_handler(callback: CallbackQuery):
    """Обработчик регистрации на мероприятие"""
    event_id = int(callback.data.split("_")[1])
    
    async for session in get_async_session():
        # Получаем пользователя и мероприятие
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        # Регистрируем пользователя на мероприятие
        success, message = await register_for_event(session, user.id, event_id)
        
        if success:
            await callback.message.answer("Вы успешно зарегистрировались на мероприятие!")
        else:
            await callback.message.answer(f"Не удалось зарегистрироваться: {message}")
        
        await callback.answer()

# Обработка отмены регистрации на мероприятие
@router.callback_query(F.data.startswith("unregister_"))
async def unregister_from_event_handler(callback: CallbackQuery):
    """Обработчик отмены регистрации на мероприятие"""
    event_id = int(callback.data.split("_")[1])
    
    async for session in get_async_session():
        # Получаем пользователя
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        # Отменяем регистрацию пользователя на мероприятие
        success, message = await unregister_from_event(session, user.id, event_id)
        
        if success:
            await callback.message.answer("Вы успешно отменили регистрацию на мероприятие.")
        else:
            await callback.message.answer(f"Не удалось отменить регистрацию: {message}")
        
        await callback.answer()