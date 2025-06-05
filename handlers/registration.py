import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode

from keyboards.main_menu import get_main_menu_keyboard
from database.db import get_async_session
from database.models import User, Gender, UserType
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError # Явный импорт IntegrityError

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
    """
    Проверяет, существует ли пользователь в базе данных по telegram_id.
    Корректно использует асинхронную сессию.
    """
    try:
        async with get_async_session() as session: # Сессия определяется здесь
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            return user is not None
    except Exception as e:
        logger.error(f"Ошибка при проверке пользователя {user_id}: {e}")
        # Здесь нет необходимости в session.rollback(), так как мы только читаем.
        return False

async def start_registration(message: Message, state: FSMContext):
    """
    Начинает процесс регистрации пользователя.
    Проверяет существование пользователя перед началом регистрации.
    """
    user_id = message.from_user.id
    
    if await check_user_exists(user_id):
        await message.answer(
            "👤 Вы уже зарегистрированы!\n\n"
            "Используйте меню для навигации по боту.",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear() 
        return
    
    welcome_text = (
        "👋 <b>Давайте знакомиться!</b>\n\n"
        "Для работы с ботом необходимо заполнить ваш профиль. "
        "Это займет всего несколько минут.\n\n"
        "🏙️ <b>Шаг 1 из 5: Укажите ваш город</b>\n\n"
        "Напишите название города, в котором вы находитесь:"
    )
    
    await message.answer(welcome_text, parse_mode=ParseMode.HTML)
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
    
    await state.update_data(city=city)
    
    await message.answer(
        f"✅ Город: <b>{city}</b>\n\n"
        f"👤 <b>Шаг 2 из 5: Как вас зовут?</b>\n\n"
        f"Введите ваше имя (или как вы хотите, чтобы вас называли в боте):",
        parse_mode=ParseMode.HTML
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
        parse_mode=ParseMode.HTML
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
            parse_mode=ParseMode.HTML
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
    
    gender = None
    gender_text = None

    if gender_input in ['М', 'МУЖСКОЙ', 'M', 'MALE']:
        gender = Gender.MALE.value
        gender_text = 'Мужской'
    elif gender_input in ['Ж', 'ЖЕНСКИЙ', 'F', 'FEMALE']:
        gender = Gender.FEMALE.value
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
        parse_mode=ParseMode.HTML
    )
    
    await state.set_state(RegistrationStates.waiting_for_about)
    logger.info(f"Пользователь {message.from_user.id} выбрал пол: {gender_text}")

@router.message(RegistrationStates.waiting_for_about)
async def process_about(message: Message, state: FSMContext):
    """Обработчик ввода информации о себе и завершение регистрации"""
    about = message.text.strip()
    
    if len(about) < 10 or len(about) > 500:
        await message.answer(
            "❌ Описание должно содержать от 10 до 500 символов.\n\n"
            "Расскажите немного о себе:"
        )
        return
    
    await state.update_data(about_me=about)
    
    user_data = await state.get_data()
    
    success = await save_user_to_db(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        user_data=user_data
    )
    
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
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_menu_keyboard()
        )
        
        await state.clear()
        logger.info(f"Пользователь {message.from_user.id} успешно зарегистрирован")
    else:
        await message.answer(
            "❌ Произошла ошибка при сохранении данных.\n\n"
            "Пожалуйста, попробуйте позже.",
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()

async def save_user_to_db(telegram_id: int, username: str | None, user_data: dict) -> bool:
    """
    Сохраняет нового пользователя в базу данных.
    Корректно использует асинхронную сессию и маппинг полей модели.
    """
    session = None # Инициализируем session здесь, чтобы она была доступна в except блоках
    try:
        async with get_async_session() as session:
            new_user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=user_data['full_name'],
                display_name=user_data['full_name'],
                city=user_data['city'],
                age=user_data['age'],
                gender=Gender(user_data['gender']),
                about=user_data['about_me'],
                rating=100,
                tokens=0,
                user_type=UserType.REGULAR
            )
            
            session.add(new_user)
            await session.commit()
            return True
            
    except IntegrityError as e:
        logger.error(f"Ошибка уникальности при сохранении пользователя {telegram_id}: {e}")
        if session: # Проверяем, что session существует, прежде чем вызывать rollback
            await session.rollback()
        return False
    except Exception as e:
        logger.error(f"Ошибка при сохранении пользователя {telegram_id}: {e}")
        if session: # Проверяем, что session существует
            await session.rollback()
        return False

# Обработчик для команды /start, если пользователь еще не зарегистрирован
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    # При старте мы начинаем регистрацию, если пользователь не существует
    await start_registration(message, state)

# Обработчик для кнопки "СТАРТ" в приветственном сообщении
@router.callback_query(F.data == "start_button")
async def handle_start_button(callback: CallbackQuery, state: FSMContext):
    # CallbackQuery не имеет message, поэтому передаем callback.message
    # Важно: callback.message может быть None, если сообщение удалено.
    # Для надежности лучше использовать callback.message, если оно есть,
    # или создать Message объект из callback.from_user
    if callback.message:
        await start_registration(callback.message, state)
    else:
        # Если message нет, создаем "фейковое" сообщение для start_registration
        # Это упрощенный подход, для более robust решения можно создать Message
        # из callback.from_user и bot
        logger.warning(f"CallbackQuery без message от пользователя {callback.from_user.id}. Попытка начать регистрацию.")
        # Может потребоваться более сложная логика, если message.text нужен
        fake_message = Message(
            message_id=callback.id, # Используем ID callback'а как ID сообщения
            from_user=callback.from_user,
            chat=callback.message.chat if callback.message else None, # Если callback.message None, chat тоже None
            date=callback.message.date if callback.message else None,
            text="/start", # Имитируем команду /start
            bot=callback.bot # Передаем объект бота, если доступен
        )
        await start_registration(fake_message, state)
        
    await callback.answer() # Важно ответить на callback_query, чтобы убрать "часики"
