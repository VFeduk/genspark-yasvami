import logging
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.menu_kb import (
    get_main_menu_keyboard, get_start_keyboard, get_event_rules_keyboard, 
    get_rules_detail_keyboard, get_back_button
)
from utils.states import MainState

router = Router()
logger = logging.getLogger(__name__)

# Определяем состояния для меню (так как их нет в utils.states)
class MenuStates(StatesGroup):
    waiting_for_rules_confirmation = State()
    showing_rules = State()

# Обработчик команды /start
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    try:
        # Попытка отправить приветственное сообщение с изображением
        welcome_image_path = os.path.join("static", "welcome.jpg")
        
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
        logger.info(f"Пользователь {message.from_user.id} запустил бота")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_start: {e}")
        await message.answer(
            "Произошла ошибка при запуске бота. Пожалуйста, попробуйте позже или обратитесь к администратору.",
            reply_markup=get_main_menu_keyboard()
        )

# Универсальный обработчик нажатия на кнопку СТАРТ
@router.callback_query(F.data == "start_bot")
async def process_start_button(callback: CallbackQuery, state: FSMContext):
    """Обработчик нажатия на кнопку СТАРТ"""
    await callback.answer()  # Подтверждаем колбэк
    
    try:
        # Проверяем текущее состояние
        current_state = await state.get_state()
        logger.info(f"Нажатие на СТАРТ от пользователя {callback.from_user.id}, текущее состояние: {current_state}")
        
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
    logger.info(f"Пользователь {message.from_user.id} нажал 'Мой профиль'")
    await message.answer("Ваш профиль. Здесь будет отображаться информация о вас и ваш рейтинг.")

@router.message(F.text == "Создать мероприятие")
async def create_event(message: Message, state: FSMContext):
    """Обработчик кнопки 'Создать мероприятие'"""
    logger.info(f"Пользователь {message.from_user.id} нажал 'Создать мероприятие'")
    await message.answer(
        "Вы должны ознакомиться с правилами публикации мероприятий и общения на площадке.",
        reply_markup=get_event_rules_keyboard()
    )
    await state.set_state(MenuStates.waiting_for_rules_confirmation)

@router.message(F.text == "Посмотреть мероприятия")
async def view_events(message: Message):
    """Обработчик кнопки 'Посмотреть мероприятия'"""
    logger.info(f"Пользователь {message.from_user.id} нажал 'Посмотреть мероприятия'")
    await message.answer("Здесь будут отображаться доступные мероприятия в вашем городе.")

@router.message(F.text == "База знаний")
async def knowledge_base(message: Message):
    """Обработчик кнопки 'База знаний'"""
    logger.info(f"Пользователь {message.from_user.id} нажал 'База знаний'")
    await message.answer(
        "Добро пожаловать в базу знаний!\n"
        "Здесь вы можете найти всю необходимую информацию о работе сервиса."
    )

# Обработчики для правил
@router.callback_query(F.data == "show_rules")
async def show_rules_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "Выберите правила для ознакомления:",
        reply_markup=get_rules_detail_keyboard()
    )
    await state.set_state(MenuStates.showing_rules)

@router.callback_query(F.data == "event_creation_rules")
async def show_creation_rules(callback: CallbackQuery):
    await callback.answer()
    rules_text = """**Правила создания мероприятий**

**1. Общие положения**
- Мероприятия должны быть направлены на общение, совместный досуг и позитивное взаимодействие.
- Запрещено создавать события с коммерческой выгодой или нарушающие законы РФ.

**2. Ограничения по содержанию**
❌ Нельзя:
- Употреблять ненормативную лексику в описании.
- Указывать контакты до подтверждения участия.

✅ Можно:
- Организовывать спортивные, творческие, развлекательные встречи.
- Указывать место, время, возрастные ограничения.

**3. Ответственность организатора**
- Вы обязуетесь быть на мероприятии в указанное время.
- При отмене уведомите участников минимум за 6 часов."""
    
    await callback.message.edit_text(
        rules_text,
        reply_markup=get_back_button()
    )

@router.callback_query(F.data == "event_registration_rules")
async def show_registration_rules(callback: CallbackQuery):
    await callback.answer()
    rules_text = """**Правила регистрации на мероприятие**

**1. Условия участия**
- Вы можете зарегистрироваться только на подходящие по возрасту и полу мероприятия.
- Нельзя записываться "на всякий случай".

**2. Поведение на мероприятии**
❌ Запрещено:
- Оскорблять других участников.
- Приходить в нетрезвом виде.

✅ Рекомендуется:
- Быть пунктуальным.
- Соблюдать договоренности.

**3. Отмена участия**
- Отменяйте запись за 12 часов до начала.
- Частые отказы снижают ваш рейтинг."""
    
    await callback.message.edit_text(
        rules_text,
        reply_markup=get_back_button()
    )

@router.callback_query(F.data == "back_to_rules")
async def back_to_rules_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Выберите правила для ознакомления:",
        reply_markup=get_rules_detail_keyboard()
    )

@router.callback_query(F.data == "accept_rules")
async def accept_rule(callback: CallbackQuery):
    await callback.answer("Вы приняли правила")
    await show_rules_menu(callback, None)

@router.callback_query(F.data == "accept_all_rules")
async def accept_all_rules(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Вы приняли все правила")
    await callback.message.answer(
        "Вы согласились со всеми правилами. Теперь вы можете создать мероприятие."
    )
    await state.clear()  # Очищаем состояние FSM

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        await callback.message.delete()  # Удаляем сообщение с правилами
    except Exception as e:
        logger.error(f"Не удалось удалить сообщение: {e}")
    
    await callback.message.answer(
        "Вернулись в главное меню. Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()  # Очищаем состояние FSM

# Обработка неизвестных сообщений
@router.message()
async def process_other_messages(message: Message):
    logger.info(f"Получено неизвестное сообщение от пользователя {message.from_user.id}: {message.text}")
    await message.answer(
        "Я не понял вашу команду. Воспользуйтесь меню или отправьте /help для получения справки."
    )

# Обработка необработанных callback_query
@router.callback_query()
async def process_unknown_callback(callback: CallbackQuery):
    logger.warning(f"Получен необработанный callback_query от пользователя {callback.from_user.id}: {callback.data}")
    await callback.answer("Эта функция находится в разработке", show_alert=True)
