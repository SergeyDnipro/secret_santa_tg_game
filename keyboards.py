from telebot import types
from telebot.types import Message

from config import buttons


def get_main_interface_keyboard(message:Message, ids=None):
    if ids is None:
        ids = []

    admin_role = message.chat.id in ids
    keyboard = admin_main_keyboard() if admin_role else user_main_keyboard()
    return keyboard


def admin_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    new_game_button = types.KeyboardButton(text=buttons.NEW_GAME_BUTTON)
    join_game_button = types.KeyboardButton(text=buttons.JOIN_GAME_BUTTON)
    lock_game_button = types.KeyboardButton(text=buttons.LOCK_GAME_BUTTON)
    keyboard.add(new_game_button, join_game_button, lock_game_button)

    start_game_button = types.KeyboardButton(text=buttons.START_GAME_BUTTON)
    keyboard.add(start_game_button)
    get_game_data_button = types.KeyboardButton(text=buttons.GET_GAME_DATA_BUTTON)
    list_games_button = types.KeyboardButton(text=buttons.LIST_GAMES_BUTTON)
    keyboard.add(list_games_button, get_game_data_button)

    return keyboard


def user_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    join_game = types.KeyboardButton(text=buttons.JOIN_GAME_BUTTON)
    keyboard.add(join_game)
    return keyboard
