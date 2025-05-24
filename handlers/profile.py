from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import POPULAR_CITIES
from database.db import get_async_session
from database.models import User, Gender, UserType
from keyboards.main_menu import get_main_menu_keyboard, get_profile_keyboard, get_gender_keyboard, get_city_keyboard
from services.user_service import get_user_by_telegram_id, create_user, update_user
from utils.states import ProfileState

router = Router()

# Обработка команды /profile
@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Обработчик команды /profile"""
    # Получаем сессию БД
    async for session in get_async_session():
        # Проверяем, зарегистрирован ли пользователь
        user = await get_user_by_telegram_id(session, message.from_user.id)
        
        if user:
            # Если пользователь уже зарегистрирован, показываем его профиль
            vip_status = "Активен" if user.is_vip else "Не активен"
            vip_until = user.vip_until.strftime("%d.%m.%Y") if user.is_vip else "—"
            
            profile_text = (
                f"<b>Ваш профиль</b>\n\n"
                f"<b>Имя:</b> {user.display_name}\n"
                f"<b>Город:</b> {user.city}\n"
                f"<b>Возраст:</b> {user.age}\n"
                f"<b>Пол:</b> {'Мужской' if user.gender == Gender.MALE else 'Женский'}\n"
                f"<b>О себе:</b> {user.about or '—'}\n\n"
                f"<b>Рейтинг:</b> {user.rating}\n"
                f"<b>Токены:</b> {user.tokens}\n"
                f"<b>VIP-статус:</b> {vip_status}\n"
                f"<b>VIP до:</b> {vip_until}\n"
            )
            
            await message.answer(profile_text, parse_mode="HTML", reply_markup=get_profile_keyboard())
        else:
            # Если пользователь не зарегистрирован, предлагаем пройти регистрацию
            await message.answer(
                "Для использования функций бота необходимо заполнить профиль.\n"
                "Давайте знакомиться! Расскажите немного о себе.",
                reply_markup=get_city_keyboard(POPULAR_CITIES)
            )
            
            # Устанавливаем состояние для начала регистрации
            await state.set_state(ProfileState.waiting_for_city)

# Обработка выбора города из списка
@router.callback_query(F.data.startswith("city_"), ProfileState.waiting_for_city)
async def process_city_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора города"""
    city = callback.data.split("_")[1]
    
    # Сохраняем город в контексте
    await state.update_data(city=city)
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Отлично! Теперь введите ваше имя:")
    
    # Переходим к следующему шагу - ввод имени
    await state.set_state(ProfileState.waiting_for_name)
    await callback.answer()

# Обработка выбора "Другой город"
@router.callback_query(F.data == "other_city", ProfileState.waiting_for_city)
async def process_other_city(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора другого города"""
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Пожалуйста, введите название вашего города:")
    
    # Переходим к состоянию ввода города вручную
    await state.set_state(ProfileState.entering_city)
    await callback.answer()

# Обработка ручного ввода города
@router.message(ProfileState.entering_city)
async def process_city_input(message: Message, state: FSMContext):
    """Обработчик ручного ввода города"""
    city = message.text.strip().capitalize()
    
    # Сохраняем город в контексте
    await state.update_data(city=city)
    
    await message.answer("Отлично! Теперь введите ваше имя:")
    
    # Переходим к следующему шагу - ввод имени
    await state.set_state(ProfileState.waiting_for_name)

# Обработка ввода имени
@router.message(ProfileState.waiting_for_name)
async def process_name_input(message: Message, state: FSMContext):
    """Обработчик ввода имени"""
    name = message.text.strip()
    
    # Проверка на корректность имени
    if len(name) < 2:
        await message.answer("Имя слишком короткое. Пожалуйста, введите более длинное имя:")
        return
    
    # Сохраняем имя в контексте
    await state.update_data(display_name=name)
    
    await message.answer("Теперь укажите ваш возраст (число):")
    
    # Переходим к следующему шагу - ввод возраста
    await state.set_state(ProfileState.waiting_for_age)

# Обработка ввода возраста
@router.message(ProfileState.waiting_for_age)
async def process_age_input(message: Message, state: FSMContext):
    """Обработчик ввода возраста"""
    try:
        age = int(message.text.strip())
        
        # Проверка на корректность возраста
        if age < 14 or age > 100:
            await message.answer("Пожалуйста, введите корректный возраст (от 14 до 100 лет):")
            return
        
        # Сохраняем возраст в контексте
        await state.update_data(age=age)
        
        # Предлагаем выбрать пол
        await message.answer("Укажите ваш пол:", reply_markup=get_gender_keyboard())
        
        # Переходим к следующему шагу - выбор пола
        await state.set_state(ProfileState.waiting_for_gender)
        
    except ValueError:
        await message.answer("Пожалуйста, введите корректный возраст (число):")

# Обработка выбора пола
@router.callback_query(F.data.startswith("gender_"), ProfileState.waiting_for_gender)
async def process_gender_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора пола"""
    gender = Gender.MALE if callback.data == "gender_male" else Gender.FEMALE
    
    # Сохраняем пол в контексте
    await state.update_data(gender=gender)
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Расскажите немного о себе (не обязательно):\n"
        "Это поможет другим пользователям узнать вас лучше."
    )
    
    # Переходим к следующему шагу - ввод информации о себе
    await state.set_state(ProfileState.waiting_for_about)
    await callback.answer()

# Обработка ввода информации о себе
@router.message(ProfileState.waiting_for_about)
async def process_about_input(message: Message, state: FSMContext):
    """Обработчик ввода информации о себе"""
    about = message.text.strip()
    
    # Сохраняем информацию о себе в контексте
    await state.update_data(about=about)
    
    # Получаем все собранные данные
    user_data = await state.get_data()
    
    # Создаем пользователя в базе данных
    async for session in get_async_session():
        await create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            city=user_data["city"],
            display_name=user_data["display_name"],
            age=user_data["age"],
            gender=user_data["gender"],
            about=user_data.get("about", "")
        )
    
    # Отправляем сообщение о успешной регистрации
    await message.answer(
        "Спасибо! Ваш профиль успешно создан.\n"
        "Теперь вы можете создавать мероприятия и участвовать в них.",
        reply_markup=get_main_menu_keyboard()
    )
    
    # Сбрасываем состояние
    await state.clear()

# Обработка нажатия на кнопку редактирования профиля
@router.callback_query(F.data == "edit_profile")
async def edit_profile(callback: CallbackQuery, state: FSMContext):
    """Обработчик нажатия на кнопку редактирования профиля"""
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Что вы хотите изменить в своем профиле?",
        reply_markup=get_edit_profile_keyboard()
    )
    await callback.answer()

# Обработка покупки VIP-статуса
@router.callback_query(F.data == "buy_vip")
async def buy_vip(callback: CallbackQuery):
    """Обработчик покупки VIP-статуса"""
    # Получаем информацию о пользователе
    async for session in get_async_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.message.answer(
                "Для покупки VIP-статуса необходимо сначала зарегистрироваться."
            )
            await callback.answer()
            return
        
        # Проверяем, достаточно ли токенов
        if user.tokens < 1500:
            await callback.message.answer(
                "Недостаточно токенов для покупки VIP-статуса.\n"
                "Необходимо: 1500 токенов, у вас: {user.tokens} токенов.\n"
                "Пополните баланс и повторите попытку."
            )
            await callback.answer()
            return
        
        # Списываем токены и активируем VIP-статус
        user.tokens -= 1500
        user.activate_vip()
        await session.commit()
        
        await callback.message.answer(
            f"Поздравляем! Вы приобрели VIP-статус до {user.vip_until.strftime('%d.%m.%Y')}.\n"
            f"Теперь вам доступны дополнительные возможности!"
        )
        await callback.answer()

# Обработка пополнения токенов
@router.callback_query(F.data == "add_tokens")
async def add_tokens(callback: CallbackQuery):
    """Обработчик пополнения токенов"""
    # Здесь должна быть интеграция с платежной системой
    # В рамках учебного проекта просто имитируем пополнение
    
    await callback.message.answer(
        "Для пополнения баланса токенов можно использовать следующие способы:\n\n"
        "1. Банковская карта\n"
        "2. Электронные кошельки\n"
        "3. Мобильный платеж\n\n"
        "Выберите удобный способ оплаты:",
        reply_markup=get_payment_methods_keyboard()
    )
    await callback.answer()