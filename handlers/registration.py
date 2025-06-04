import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.menu_kb import get_main_menu_keyboard
from database.db import get_async_session
from database.models import User
from sqlalchemy import select

router = Router()
logger = logging.getLogger(__name__)

# Состояния для регистрации
class RegistrationStates(StatesGroup):
    waiting_for_city = State()
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_gender = State()
    waiting_for_about = State()

async def check_user_exists(user_id: int) -> bool:
    """Проверяет, существует ли пользователь в базе данных"""
    try:
        # Правильная работа с сессией
        async_session_factory = get_async_session()
        async with async_session_factory() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            return user is not None
    except Exception as e:
        logger.error(f"Ошибка при проверке пользователя {user_id}: {e}")
        return False

async def start_registration(message: Message, state: FSMContext):
    """Начинает процесс регистрации пользователя"""
    user_id = message.from_user.id
    
    # Проверяем, не зарегистрирован ли уже пользователь
    if await check_user_exists(user_id):
        await message.answer(
            "👤 Вы уже зарегистрированы!\n\n"
            "Используйте меню для навигации по боту.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Начинаем регистрацию
    welcome_text = (
        "👋 <b>Давайте знакомиться!</b>\n\n"
        "Для работы с ботом необходимо заполнить ваш профиль. "
        "Это займет всего несколько минут.\n\n"
        "🏙️ <b>Шаг 1 из 5: Укажите ваш город</b>\n\n"
        "Напишите название города, в котором вы находитесь:"
    )
    
    await message.answer(welcome_text, parse_mode="HTML")
    await state.set_state(RegistrationStates.waiting_for_city)
    logger.info(f"Пользователь {user_id} начал регистрацию")

# Обработчик ввода города
@router.message(RegistrationStates.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    """Обработчик ввода города"""
    city = message.text.strip().title()
    
    if len(city) < 2 or len(city) > 50:
        await message.answer(
            "❌ Некорректное название города.\n\n"
            "Пожалуйста, введите правильное название города (от 2 до 50 символов):"
        )
        return
    
    # Сохраняем город
    await state.update_data(city=city)
    
    await message.answer(
        f"✅ Город: <b>{city}</b>\n\n"
        f"👤 <b>Шаг 2 из 5: Как вас зовут?</b>\n\n"
        f"Введите ваше имя (или как вы хотите, чтобы вас называли в боте):",
        parse_mode="HTML"
    )
    
    await state.set_state(RegistrationStates.waiting_for_name)
    logger.info(f"Пользователь {message.from_user.id} ввел город: {city}")

@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Обработчик ввода имени"""
    name = message.text.strip()
    
    if len(name) < 2 or len(name) > 30:
        await message.answer(
            "❌ Некорректное имя.\n\n"
            "Пожалуйста, введите имя от 2 до 30 символов:"
        )
        return
    
    await state.update_data(full_name=name)
    
    await message.answer(
        f"✅ Имя: <b>{name}</b>\n\n"
        f"🎂 <b>Шаг 3 из 5: Сколько вам лет?</b>\n\n"
        f"Введите ваш возраст (от 16 до 80 лет):",
        parse_mode="HTML"
    )
    
    await state.set_state(RegistrationStates.waiting_for_age)
    logger.info(f"Пользователь {message.from_user.id} ввел имя: {name}")

@router.message(RegistrationStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    """Обработчик ввода возраста"""
    try:
        age = int(message.text.strip())
        
        if age < 16 or age > 80:
            await message.answer(
                "❌ Некорректный возраст.\n\n"
                "Пожалуйста, введите возраст от 16 до 80 лет:"
            )
            return
        
        await state.update_data(age=age)
        
        await message.answer(
            f"✅ Возраст: <b>{age} лет</b>\n\n"
            f"👫 <b>Шаг 4 из 5: Укажите ваш пол</b>\n\n"
            f"Напишите 'М' для мужского пола или 'Ж' для женского:",
            parse_mode="HTML"
        )
        
        await state.set_state(RegistrationStates.waiting_for_gender)
        logger.info(f"Пользователь {message.from_user.id} ввел возраст: {age}")
        
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введите возраст числом.\n\n"
            "Например: 25"
        )

@router.message(RegistrationStates.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext):
    """Обработчик выбора пола"""
    gender_input = message.text.strip().upper()
    
    if gender_input in ['М', 'МУЖСКОЙ', 'M', 'MALE']:
        gender = 'male'
        gender_text = 'Мужской'
    elif gender_input in ['Ж', 'ЖЕНСКИЙ', 'F', 'FEMALE']:
        gender = 'female'
        gender_text = 'Женский'
    else:
        await message.answer(
            "❌ Пожалуйста, напишите 'М' для мужского пола или 'Ж' для женского пола:"
        )
        return
    
    await state.update_data(gender=gender)
    
    await message.answer(
        f"✅ Пол: <b>{gender_text}</b>\n\n"
        f"📝 <b>Шаг 5 из 5: Расскажите о себе</b>\n\n"
        f"Напишите несколько слов о себе, ваших интересах или хобби "
        f"(от 10 до 500 символов):",
        parse_mode="HTML"
    )
    
    await state.set_state(RegistrationStates.waiting_for_about)
    logger.info(f"Пользователь {message.from_user.id} выбрал пол: {gender_text}")

@router.message(RegistrationStates.waiting_for_about)
async def process_about(message: Message, state: FSMContext):
    """Обработчик ввода информации о себе"""
    about = message.text.strip()
    
    if len(about) < 10 or len(about) > 500:
        await message.answer(
            "❌ Описание должно содержать от 10 до 500 символов.\n\n"
            "Расскажите немного о себе:"
        )
        return
    
    # Сохраняем информацию о себе
    await state.update_data(about_me=about)
    
    # Получаем все данные
    user_data = await state.get_data()
    
    # Сохраняем пользователя в базу данных
    success = await save_user_to_db(message.from_user.id, message.from_user.username, user_data)
    
    if success:
        summary_text = (
            f"🎉 <b>Регистрация завершена!</b>\n\n"
            f"📋 <b>Ваш профиль:</b>\n"
            f"🏙️ Город: {user_data['city']}\n"
            f"👤 Имя: {user_data['full_name']}\n"
            f"🎂 Возраст: {user_data['age']} лет\n"
            f"👫 Пол: {'Мужской' if user_data['gender'] == 'male' else 'Женский'}\n\n"
            f"⭐ Ваш начальный рейтинг: 100 баллов\n\n"
            f"Теперь вы можете создавать мероприятия и участвовать в событиях!"
        )
        
        await message.answer(
            summary_text,
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
        
        await state.clear()
        logger.info(f"Пользователь {message.from_user.id} успешно зарегистрирован")
    else:
        await message.answer(
            "❌ Произошла ошибка при сохранении данных.\n\n"
            "Пожалуйста, попробуйте позже.",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()

async def save_user_to_db(telegram_id: int, username: str, user_data: dict) -> bool:
    """Сохраняет пользователя в базу данных"""
    try:
        # Правильная работа с сессией
        async_session_factory = get_async_session()
        async with async_session_factory() as session:
            new_user = User(
                telegram_id=telegram_id,
                username=username,
                full_name=user_data['full_name'],
                city=user_data['city'],
                age=user_data['age'],
                gender=user_data['gender'],
                about_me=user_data['about_me'],
                rating=100
            )
            
            session.add(new_user)
            await session.commit()
            return True
            
    except Exception as e:
        logger.error(f"Ошибка при сохранении пользователя {telegram_id}: {e}")
        return False
