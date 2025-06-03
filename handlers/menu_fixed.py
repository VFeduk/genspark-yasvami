import logging
import os
from handlers.registration import start_registration, check_user_exists
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

# Определяем состояния для меню
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
            "Произошла ошибка при запуске бота. Пожалуйста, попробуйте позже.",
            reply_markup=get_main_menu_keyboard()
        )

# Обработчик команды /help
@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "🌟 <b>Добро пожаловать в бот \"Я с Вами\"!</b> 🌟\n\n"
        "Этот бот поможет вам найти компанию для любого вида досуга или организовать свое мероприятие!\n\n"
        "<b>Основные возможности:</b>\n"
        "• 👥 Найти новых друзей по интересам\n"
        "• 🎉 Создать собственное мероприятие\n"
        "• 🔍 Найти интересные события в вашем городе\n"
        "• ⭐ Система рейтинга для качественного сообщества\n\n"
        "<b>Как начать:</b>\n"
        "1. Нажмите кнопку \"Мой профиль\" для регистрации\n"
        "2. Заполните информацию о себе\n"
        "3. Создайте мероприятие или найдите подходящее\n"
        "4. Знакомьтесь и проводите время интересно!\n\n"
        "<b>Нужна помощь?</b> Перейдите в \"База знаний\" для подробной информации."
    )
    
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())

# Универсальный обработчик нажатия на кнопку СТАРТ
@router.callback_query(F.data == "start_bot")
async def process_start_button(callback: CallbackQuery, state: FSMContext):
    """Обработчик нажатия на кнопку СТАРТ"""
    await callback.answer()  # Подтверждаем колбэк
    
    try:
        # Проверяем текущее состояние
        current_state = await state.get_state()
        logger.info(f"Нажатие на СТАРТ от пользователя {callback.from_user.id}, текущее состояние: {current_state}")
        
        # Отправляем расширенное сообщение с главным меню
        welcome_text = (
            "🎉 <b>Добро пожаловать в главное меню!</b>\n\n"
            "Выберите нужный раздел из меню ниже:\n\n"
            "👤 <b>Мой профиль</b> - управление вашими данными и рейтингом\n"
            "➕ <b>Создать мероприятие</b> - организуйте свое событие\n"
            "👀 <b>Посмотреть мероприятия</b> - найдите интересные события\n"
            "📚 <b>База знаний</b> - правила и инструкции\n\n"
            "💡 <i>Если вы впервые здесь, рекомендуем начать с заполнения профиля и изучения базы знаний!</i>"
        )
        
        await callback.message.answer(
            welcome_text,
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
        
        # Сбрасываем состояние
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка в process_start_button: {e}")
        await callback.message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз или отправьте /start для перезапуска.",
            reply_markup=get_main_menu_keyboard()
        )

# Обработчики команд из меню бота (команды /profile, /create и т.д.)
@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Обработчик команды /profile"""
    await show_profile(message)

@router.message(Command("create"))
async def cmd_create(message: Message, state: FSMContext):
    """Обработчик команды /create"""
    await create_event(message, state)

@router.message(Command("events"))
async def cmd_events(message: Message):
    """Обработчик команды /events"""
    await view_events(message)

@router.message(Command("knowledge"))
async def cmd_knowledge(message: Message):
    """Обработчик команды /knowledge"""
    await knowledge_base(message)

# Обработчики для кнопок главного меню с ReplyKeyboard
@router.message(F.text == "Мой профиль")
async def show_profile(message: Message, state: FSMContext):
    """Обработчик кнопки 'Мой профиль'"""
    logger.info(f"Пользователь {message.from_user.id} нажал 'Мой профиль'")
    
    # Проверяем, зарегистрирован ли пользователь
    if not await check_user_exists(message.from_user.id):
        await start_registration(message, state)
    else:
        # Показываем существующий профиль (пока заглушка)
        await message.answer(
            "👤 <b>Ваш профиль</b>\n\n"
            "Здесь будет отображаться ваша информация.\n"
            "Функция просмотра и редактирования профиля будет добавлена в следующем обновлении.",
 @router.message(F.text == "Мой профиль")
async def show_profile(message: Message, state: FSMContext):
    """Обработчик кнопки 'Мой профиль'"""
    logger.info(f"Пользователь {message.from_user.id} нажал 'Мой профиль'")
    
    # Проверяем, зарегистрирован ли пользователь
    if not await check_user_exists(message.from_user.id):
        await start_registration(message, state)
    else:
        await message.answer(
            "👤 <b>Ваш профиль</b>\n\n"
            "Информация о вашем профиле загружается...\n"
            "Функция просмотра и редактирования профиля будет добавлена в следующем обновлении.",
            parse_mode="HTML"
        )

    rules_text = (
        "📋 <b>Создание мероприятия</b>\n\n"
        "Перед созданием мероприятия вы должны ознакомиться с правилами "
        "публикации мероприятий и общения на площадке.\n\n"
        "Это поможет создать качественное сообщество и обеспечить "
        "безопасность всех участников."
    )
    
    await message.answer(
        rules_text,
        parse_mode="HTML",
        reply_markup=get_event_rules_keyboard()
    )
    await state.set_state(MenuStates.waiting_for_rules_confirmation)

@router.message(F.text == "Посмотреть мероприятия")
async def view_events(message: Message):
    """Обработчик кнопки 'Посмотреть мероприятия'"""
    logger.info(f"Пользователь {message.from_user.id} нажал 'Посмотреть мероприятия'")
    
    events_text = (
        "👀 <b>Мероприятия</b>\n\n"
        "Здесь будут отображаться доступные мероприятия в вашем городе:\n"
        "• Прогулки и встречи\n"
        "• Спортивные активности\n"
        "• Творческие мероприятия\n"
        "• Путешествия и поездки\n\n"
        "🔧 <i>Функция просмотра мероприятий находится в разработке</i>"
    )
    
    await message.answer(events_text, parse_mode="HTML")

@router.message(F.text == "База знаний")
async def knowledge_base(message: Message):
    """Обработчик кнопки 'База знаний'"""
    logger.info(f"Пользователь {message.from_user.id} нажал 'База знаний'")
    
    knowledge_text = (
        "📚 <b>База знаний</b>\n\n"
        "Добро пожаловать в базу знаний бота \"Я с Вами\"!\n\n"
        "Здесь вы найдете всю необходимую информацию:\n"
        "• Правила создания мероприятий\n"
        "• Правила участия в событиях\n"
        "• Информацию о системе рейтинга\n"
        "• Возможности VIP-статуса\n"
        "• Общую информацию о проекте\n\n"
        "📖 Выберите интересующий вас раздел:"
    )
    
    # Здесь можно добавить inline-клавиатуру для выбора разделов базы знаний
    await message.answer(knowledge_text, parse_mode="HTML")

# Обработчики для правил (остаются без изменений)
@router.callback_query(F.data == "show_rules")
async def show_rules_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "📋 Выберите правила для ознакомления:",
        reply_markup=get_rules_detail_keyboard()
    )
    await state.set_state(MenuStates.showing_rules)

@router.callback_query(F.data == "event_creation_rules")
async def show_creation_rules(callback: CallbackQuery):
    await callback.answer()
    rules_text = """📋 <b>Правила создания мероприятий</b>

<b>1. Общие положения</b>
• Мероприятия должны быть направлены на общение, совместный досуг и позитивное взаимодействие
• Запрещено создавать события с коммерческой выгодой или нарушающие законы РФ
• Все участники должны чувствовать себя комфортно и безопасно

<b>2. Ограничения по содержанию</b>
❌ <b>Нельзя:</b>
• Употреблять ненормативную лексику в описании
• Указывать контакты до подтверждения участия
• Размещать контент 18+ или провокационного характера

✅ <b>Можно:</b>
• Организовывать спортивные, творческие, развлекательные встречи
• Указывать место, время, возрастные ограничения
• Просить участников взять необходимые вещи

<b>3. Ответственность организатора</b>
• Вы обязуетесь быть на мероприятии в указанное время
• При отмене уведомите участников минимум за 6 часов
• Несоблюдение правил ведет к снижению рейтинга"""
    
    await callback.message.edit_text(
        rules_text,
        parse_mode="HTML",
        reply_markup=get_back_button()
    )

@router.callback_query(F.data == "event_registration_rules")
async def show_registration_rules(callback: CallbackQuery):
    await callback.answer()
    rules_text = """📋 <b>Правила регистрации на мероприятие</b>

<b>1. Условия участия</b>
• Вы можете зарегистрироваться только на подходящие по возрасту и полу мероприятия
• Нельзя записываться "на всякий случай" - если не уверены, лучше не занимайте место

<b>2. Поведение на мероприятии</b>
❌ <b>Запрещено:</b>
• Оскорблять других участников
• Приходить в нетрезвом виде
• Покидать мероприятие без предупреждения

✅ <b>Рекомендуется:</b>
• Быть пунктуальным и уважать время других
• Соблюдать договоренности
• Оставить честный отзыв после мероприятия

<b>3. Отмена участия</b>
• Отменяйте запись за 12 часов до начала
• Частые отказы в последний момент снижают рейтинг

<b>Последствия нарушений:</b>
• Первое нарушение → предупреждение
• Повторное → снижение рейтинга (-10 баллов)
• Систематические нарушения → блокировка"""
    
    await callback.message.edit_text(
        rules_text,
        parse_mode="HTML",
        reply_markup=get_back_button()
    )

@router.callback_query(F.data == "back_to_rules")
async def back_to_rules_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "📋 Выберите правила для ознакомления:",
        reply_markup=get_rules_detail_keyboard()
    )

@router.callback_query(F.data == "accept_rules")
async def accept_rule(callback: CallbackQuery):
    await callback.answer("Вы приняли правила")
    await show_rules_menu(callback, None)

@router.callback_query(F.data == "accept_all_rules")
async def accept_all_rules(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Вы приняли все правила")
    
    success_text = (
        "✅ <b>Отлично!</b>\n\n"
        "Вы согласились со всеми правилами. Теперь вы можете создать мероприятие.\n\n"
        "🔧 <i>Функция создания мероприятий находится в разработке.</i>\n"
        "Пока вы можете изучить другие разделы бота."
    )
    
    await callback.message.answer(
        success_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception as e:
        logger.error(f"Не удалось удалить сообщение: {e}")
    
    await callback.message.answer(
        "🏠 Вы вернулись в главное меню. Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()

# Обработка неизвестных сообщений
@router.message()
async def process_other_messages(message: Message):
    if message.text and message.text.startswith('/'):
        logger.info(f"Получена неизвестная команда от пользователя {message.from_user.id}: {message.text}")
        await message.answer(
            "❓ Неизвестная команда.\n\n"
            "Используйте меню ниже для навигации или отправьте /help для получения справки.",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        logger.info(f"Получено неизвестное сообщение от пользователя {message.from_user.id}: {message.text}")
        await message.answer(
            "Я не понял вашу команду. Воспользуйтесь меню ниже или отправьте /help для получения справки.",
            reply_markup=get_main_menu_keyboard()
        )

# Обработка необработанных callback_query
@router.callback_query()
async def process_unknown_callback(callback: CallbackQuery):
    logger.warning(f"Получен необработанный callback_query от пользователя {callback.from_user.id}: {callback.data}")
    await callback.answer("🔧 Эта функция находится в разработке", show_alert=True)
