import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from keyboards.menu_kb import (
    get_main_menu_keyboard, get_start_keyboard, get_event_rules_keyboard, 
    get_rules_detail_keyboard, get_back_button
)
from database.db import get_async_session
from database.models import User

# Создаем роутер для обработчиков меню
router = Router()
logger = logging.getLogger(__name__)

# Состояния для FSM
class MenuStates(StatesGroup):
    waiting_for_rules_confirmation = State()
    showing_rules = State()

# Обработчик команды /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    # Отправляем приветственное сообщение с фото
    with open("static/welcome_image.jpg", "rb") as photo:
        await message.answer_photo(
            photo,
            caption=(
                "Привет! Это бот для поиска и организации неформальных "
                "мероприятий! Здесь ты можешь найти новых друзей, компанию "
                "для любого вида досуга или найти единомышленников на своем пути!) "
                "В общем нажимай кнопку \"СТАРТ\" и поехали!"
            ),
            reply_markup=get_start_keyboard()
        )

# Обработчик нажатия на кнопку "СТАРТ"
@router.callback_query(Text("start_bot"))
async def process_start_button(callback: CallbackQuery):
    await callback.answer()  # Подтверждаем колбэк

    # Отправляем сообщение с главным меню
    await callback.message.answer(
        "Добро пожаловать в главное меню!",
        reply_markup=get_main_menu_keyboard()
    )

# Обработчик кнопки "Мой профиль"
@router.message(Text("Мой профиль"))
async def show_profile(message: Message):
    # Здесь будет логика получения данных профиля
    await message.answer(
        "Ваш профиль. Здесь будет отображаться информация о вас и ваш рейтинг."
    )
    # Дальше можно добавить логику отображения профиля

# Обработчик кнопки "Создать мероприятие"
@router.message(Text("Создать мероприятие"))
async def create_event(message: Message, state: FSMContext):
    # Отправляем сообщение о необходимости ознакомиться с правилами
    await message.answer(
        "Вы должны ознакомиться с правилами публикации мероприятий и общения на площадке.",
        reply_markup=get_event_rules_keyboard()
    )
    # Устанавливаем состояние ожидания подтверждения правил
    await state.set_state(MenuStates.waiting_for_rules_confirmation)

# Обработчик кнопки "Посмотреть мероприятия"
@router.message(Text("Посмотреть мероприятия"))
async def view_events(message: Message):
    # Здесь будет логика получения и отображения мероприятий
    await message.answer(
        "Здесь будут отображаться доступные мероприятия в вашем городе."
    )
    # Можно добавить логику отображения списка мероприятий

# Обработчик кнопки "База знаний"
@router.message(Text("База знаний"))
async def knowledge_base(message: Message):
    # Отображаем базу знаний
    await message.answer(
        "Добро пожаловать в базу знаний!\n"
        "Здесь вы можете найти всю необходимую информацию о работе сервиса."
    )
    # Можно добавить кнопки для навигации по базе знаний

# Обработчики для правил
@router.callback_query(Text("show_rules"))
async def show_rules_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "Выберите правила для ознакомления:",
        reply_markup=get_rules_detail_keyboard()
    )
    await state.set_state(MenuStates.showing_rules)

@router.callback_query(Text("event_creation_rules"))
async def show_creation_rules(callback: CallbackQuery):
    await callback.answer()
    rules_text = """
### **Правила создания мероприятий**

### **1. Общие положения**

- Мероприятия должны быть направлены на **общение, совместный досуг и позитивное взаимодействие**.
- **Запрещено** создавать события с коммерческой выгодой (продажи, реклама услуг), а также мероприятия, нарушающие законы РФ.
- Все участники должны чувствовать себя **комфортно и безопасно**.

### **2. Ограничения по содержанию**

❌ **Нельзя**:

- Употреблять ненормативную лексику в описании.
- Указывать контакты (телефоны, соцсети) до подтверждения участия.
- Размещать мероприятия с **политической, религиозной** или **экстремистской** повесткой.
- Публиковать контент **18+** или провокационного характера.

✅ **Можно**:

- Организовывать **спортивные, творческие, развлекательные** и другие **дружеские** встречи.
- Указывать **место, время, возрастные ограничения** и другую полезную информацию.
- Просить участников взять с собой что-то необходимое (еду, инвентарь).

### **3. Ответственность организатора**

- Вы **обязуетесь** быть на мероприятии в указанное время.
- Если мероприятие **отменяется**, необходимо уведомить участников **минимум за 6 часов**.
- Несоблюдение правил ведет к **снижению рейтинга** или **блокировке**.
"""
    await callback.message.edit_text(
        rules_text,
        reply_markup=get_back_button()
    )

@router.callback_query(Text("event_registration_rules"))
async def show_registration_rules(callback: CallbackQuery):
    await callback.answer()
    rules_text = """
### **Правила регистрации на мероприятие**

### **1. Условия участия**

- Вы можете зарегистрироваться **только на мероприятия, подходящие вам по возрасту и полу** (если организатор указал ограничения).
- **Нельзя** записываться "на всякий случай" – если вы не уверены, что придете, лучше не занимайте место.

### **2. Поведение на мероприятии**

❌ **Запрещено**:

- Оскорблять, дискриминировать или нарушать личные границы других участников.
- Приходить в **нетрезвом виде** или под воздействием запрещенных веществ.
- Покидать мероприятие **без предупреждения**, если от вас зависит его проведение (например, вы – водитель или организатор).

✅ **Рекомендуется**:

- Быть **пунктуальным** и уважать время других.
- Соблюдать **договоренности** (например, взять с собой то, о чем договорились).
- После мероприятия **оставить честный отзыв** об организаторе и участниках.

### **3. Отмена участия**

- Если вы передумали, **отмените запись** за **12 часов** до начала.
- Частые отказы в последний момент могут **понизить ваш рейтинг**.

---

### **Последствия нарушений**

- **Первое нарушение** → **предупреждение** от бота.
- **Повторное нарушение** → **снижение рейтинга** (-10 баллов).
- **Систематические нарушения** → **блокировка** возможности создавать/участвовать в мероприятиях.
"""
    await callback.message.edit_text(
        rules_text,
        reply_markup=get_back_button()
    )

@router.callback_query(Text("back_to_rules"))
async def back_to_rules_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Выберите правила для ознакомления:",
        reply_markup=get_rules_detail_keyboard()
    )

@router.callback_query(Text("accept_rules"))
async def accept_rule(callback: CallbackQuery):
    await callback.answer("Вы приняли правила")
    await show_rules_menu(callback, None)

@router.callback_query(Text("accept_all_rules"))
async def accept_all_rules(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Вы приняли все правила")
    await callback.message.answer(
        "Вы согласились со всеми правилами. Теперь вы можете создать мероприятие."
        # Здесь можно запускать процесс создания мероприятия
    )
    await state.clear()  # Очищаем состояние FSM

@router.callback_query(Text("back_to_main"))
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()  # Удаляем сообщение с правилами
    await callback.message.answer(
        "Вернулись в главное меню. Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()  # Очищаем состояние FSM

# Обработка неизвестных сообщений
@router.message()
async def process_other_messages(message: Message):
    logger.info(f"Получено неизвестное сообщение: {message.text}")
    await message.answer(
        "Я не понял вашу команду. Воспользуйтесь меню или отправьте /help для получения справки."
    )
