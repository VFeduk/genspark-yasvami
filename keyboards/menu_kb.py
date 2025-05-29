from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard():
    """Основное меню бота с кнопками для основных разделов"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мой профиль")],
            [KeyboardButton(text="Создать мероприятие")],
            [KeyboardButton(text="Посмотреть мероприятия")],
            [KeyboardButton(text="База знаний")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard

def get_start_keyboard():
    """Клавиатура с кнопкой СТАРТ для начального сообщения"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="СТАРТ", callback_data="start_bot")]
        ]
    )
    return keyboard

def get_event_rules_keyboard():
    """Клавиатура для правил мероприятий"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Ознакомиться", callback_data="show_rules")],
            [InlineKeyboardButton(text="Согласен со всем", callback_data="accept_all_rules")],
            [InlineKeyboardButton(text="Назад", callback_data="back_to_main")]
        ]
    )
    return keyboard

def get_rules_detail_keyboard():
    """Клавиатура для просмотра правил"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Правила создания мероприятий", callback_data="event_creation_rules")],
            [InlineKeyboardButton(text="Правила регистрации на мероприятие", callback_data="event_registration_rules")],
            [InlineKeyboardButton(text="Всё прочитал, со всем согласен", callback_data="accept_all_rules")]
        ]
    )
    return keyboard

def get_back_button():
    """Кнопка "Назад" для возврата в предыдущее меню"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Согласен", callback_data="accept_rules")],
            [InlineKeyboardButton(text="Назад", callback_data="back_to_rules")]
        ]
    )
    return keyboard

def get_city_selection_keyboard(cities: list):
    """Клавиатура для выбора города из списка"""
    rows = []
    # Добавляем города по 2 в ряд
    for i in range(0, len(cities), 2):
        if i + 1 < len(cities):
            rows.append([
                KeyboardButton(text=cities[i]), 
                KeyboardButton(text=cities[i+1])
            ])
        else:
            rows.append([KeyboardButton(text=cities[i])])
    
    # Добавляем кнопку "Другой город"
    rows.append([KeyboardButton(text="Другой город")])
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def get_gender_selection_keyboard():
    """Клавиатура для выбора пола аудитории мероприятия"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👦 Парни", callback_data="gender_male"),
                InlineKeyboardButton(text="👧 Девушки", callback_data="gender_female")
            ],
            [InlineKeyboardButton(text="👫 Все", callback_data="gender_all")],
            [InlineKeyboardButton(text="Назад", callback_data="back_to_event_step1")]
        ]
    )
    return keyboard

def get_purpose_keyboard():
    """Клавиатура для выбора цели мероприятия"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пошли гулять", callback_data="purpose_walk")],
            [InlineKeyboardButton(text="Давайте знакомиться", callback_data="purpose_meet")],
            [InlineKeyboardButton(text="Совместные поездки/путешествия", callback_data="purpose_travel")],
            [InlineKeyboardButton(text="Друзья мне нужна помощь", callback_data="purpose_help")],
            [InlineKeyboardButton(text="Пойдем тусить", callback_data="purpose_party")],
            [InlineKeyboardButton(text="Назад", callback_data="back_to_city_selection")]
        ]
    )
    return keyboard
