import logging
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from config import STATIC_DIR
from keyboards.menu_kb import (
    get_main_menu_keyboard, get_start_keyboard, get_event_rules_keyboard, 
    get_rules_detail_keyboard, get_back_button
)
from utils.states import MainState, MenuStates

router = Router()
logger = logging.getLogger(__name__)

# Обработчик команды /start
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    try:
        # Попытка отправить приветственное сообщение с изображением
        welcome_image_path = os.path.join(STATIC_DIR, "welcome_image.jpg")
        if os.path.exists(welcome_image_path):
            welcome_image = FSInputFile(welcome_image_path)
            await message.answer_photo(
                photo=welcome_image,
                caption="Привет! Это бот для поиска и организации неформальных мероприятий! "
                        "Здесь ты можешь найти новых друзей, компанию для любого вида досуга "
                        "или найти единомышленников на своем пути!) В общем нажимай кнопку \"СТАРТ\" и поехали!",
                reply_markup=get_start_keyboard()
            )
        else:
            # Отправка без изображения, если файл не найден
            logger.warning(f"Изображение не найдено: {welcome_image_path}")
            await message.answer(
                "Привет! Это бот для поиска и организации неформальных мероприятий! "
                "Здесь ты можешь найти новых друзей, компанию для любого вида досуга "
                "или найти единомышленников на своем пути!) В общем нажимай кнопку \"СТАРТ\" и поехали!",
                reply_markup=get_start_keyboard()
            )
        
        # Устанавливаем состояние ожидания нажатия кнопки "СТАРТ"
        await state.set_state(MainState.waiting_for_start)
    except Exception as e:
        logger.error(f"Ошибка в cmd_start: {e}")
        await message.answer(
            "Произошла ошибка при запуске бота. Пожалуйста, попробуйте позже или обратитесь к администратору.",
            reply_markup=get_main_menu_keyboard()
        )

# Универсальный обработчик нажатия на кнопку СТАРТ - работает в любом состоянии
@router.callback_query(F.data == "start_bot")
async def process_start_button(callback: CallbackQuery, state: FSMContext):
    """Обработчик нажатия на кнопку СТАРТ"""
    await callback.answer()  # Подтверждаем колбэк
    
    try:
        # Проверяем текущее состояние
        current_state = await state.get_state()
        logger.info(f"Нажатие на СТАРТ, текущее состояние: {current_state}")
        
        # Отправляем сообщение с главным меню
        await callback.message.answer(
            "Добро пожаловать в главное меню!",
            reply_markup=get_main_menu_keyboard()
        )
        
        # Сбрасываем состояние
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка в process_start_button: {e}")
        await callback.message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз или отправьте /start для перезапуска."
        )

# Обработчики для кнопок главного меню с ReplyKeyboard
@router.message(F.text == "Мой профиль")
async def show_profile(message: Message):
    """Обработчик кнопки 'Мой профиль'"""
    logger.info("Нажата кнопка 'Мой профиль'")
    await message.answer("Ваш профиль. Здесь будет отображаться информация о вас и ваш рейтинг.")

@router.message(F.text == "Создать мероприятие")
async def create_event(message: Message, state: FSMContext):
    """Обработчик кнопки 'Создать мероприятие'"""
    logger.info("Нажата кнопка 'Создать мероприятие'")
    await message.answer(
        "Вы должны ознакомиться с правилами публикации мероприятий и общения на площадке.",
        reply_markup=get_event_rules_keyboard()
    )
    await state.set_state(MenuStates.waiting_for_rules_confirmation)

@router.message(F.text == "Посмотреть мероприятия")
async def view_events(message: Message):
    """Обработчик кнопки 'Посмотреть мероприятия'"""
    logger.info("Нажата кнопка 'Посмотреть мероприятия'")
    await message.answer("Здесь будут отображаться доступные мероприятия в вашем городе.")

@router.message(F.text == "База знаний")
async def knowledge_base(message: Message):
    """Обработчик кнопки 'База знаний'"""
    logger.info("Нажата кнопка 'База знаний'")
    await message.answer(
        "Добро пожаловать в базу знаний!\n"
        "Здесь вы можете найти всю необходимую информацию о работе сервиса."
    )
