from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_event_creation_rules_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для правил создания мероприятий"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ознакомиться", callback_data="view_rules")],
        [InlineKeyboardButton(text="Согласен со всем", callback_data="agree_rules")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main")]
    ])
    return keyboard

def get_confirmation_keyboard(confirm_type: str) -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения (правил или создания мероприятия)"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтверждаю", callback_data=f"confirm_{confirm_type}")],
        [InlineKeyboardButton(text="Отмена", callback_data="back_to_main")]
    ])
    return keyboard

def get_event_purpose_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора цели мероприятия"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пошли гулять", callback_data="purpose_walk")],
        [InlineKeyboardButton(text="Давайте знакомиться", callback_data="purpose_meet")],
        [InlineKeyboardButton(text="Совместные поездки/путешествия", callback_data="purpose_travel")],
        [InlineKeyboardButton(text="Друзья мне нужна помощь", callback_data="purpose_help")],
        [InlineKeyboardButton(text="Пойдем тусить", callback_data="purpose_party")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main")]
    ])
    return keyboard

def get_event_target_audience_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора целевой аудитории мероприятия"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨 Только для мужчин", callback_data="audience_male")],
        [InlineKeyboardButton(text="👩 Только для женщин", callback_data="audience_female")],
        [InlineKeyboardButton(text="👨‍👩‍👧 Для всех", callback_data="audience_all")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main")]
    ])
    return keyboard

def get_event_age_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора возрастных ограничений"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Указать возраст", callback_data="specify_age")],
        [InlineKeyboardButton(text="Без ограничений", callback_data="no_age_limits")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main")]
    ])
    return keyboard

def get_event_registration_keyboard(event_id: int, can_register: bool = True) -> InlineKeyboardMarkup:
    """Клавиатура для регистрации на мероприятие"""
    buttons = []
    
    if can_register:
        buttons.append([InlineKeyboardButton(text="Я пойду!", callback_data=f"register_{event_id}")])
    else:
        buttons.append([InlineKeyboardButton(text="Нельзя зарегистрироваться", callback_data=f"cant_register_{event_id}")])
    
    buttons.append([InlineKeyboardButton(text="Отменить регистрацию", callback_data=f"unregister_{event_id}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
