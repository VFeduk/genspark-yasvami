from aiogram.fsm.state import StatesGroup, State

class MainState(StatesGroup):
    """Состояния основного меню"""
    waiting_for_start = State()

class ProfileState(StatesGroup):
    """Состояния для регистрации пользователя"""
    waiting_for_city = State()
    entering_city = State()
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_gender = State()
    waiting_for_about = State()
    
    # Состояния для редактирования профиля
    editing_city = State()
    editing_name = State()
    editing_age = State()
    editing_about = State()

class EventCreationState(StatesGroup):
    """Состояния для создания мероприятия"""
    waiting_for_rules_agreement = State()
    waiting_for_city = State()
    waiting_for_purpose = State()
    waiting_for_target_audience = State()
    waiting_for_age_limits = State()
    entering_min_age = State()
    entering_max_age = State()
    entering_title = State()
    entering_description = State()
    entering_datetime = State()
    entering_max_participants = State()
    confirming_event = State()

class EventViewState(StatesGroup):
    """Состояния для просмотра мероприятий"""
    selecting_city = State()
    viewing_events = State()

class RatingState(StatesGroup):
    """Состояния для оценки пользователей"""
    selecting_event = State()
    selecting_rating = State()
