from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def confirmation_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="To'g'ri✅", callback_data='correct'))
    keyboard.add(InlineKeyboardButton(text="Noto'g'ri❌", callback_data='incorrect'))
    return keyboard

def admin_keyboard(user_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Tasdiqlash✅", callback_data=f'admin_approve_{user_id}'))
    keyboard.add(InlineKeyboardButton(text="Rad etish❌", callback_data=f'admin_reject_{user_id}'))
    return keyboard

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def direction_keyboard():
    keyboard = InlineKeyboardMarkup()
    directions = ["frontend🧳", "backend⚙️", "dizayn🧑‍🎨", "beginner▶️", "3d🎲"]
    for direction in directions:
        keyboard.add(InlineKeyboardButton(text=direction, callback_data=f'direction_{direction}'))
    return keyboard


