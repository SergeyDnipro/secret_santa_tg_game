import types
import keyboards
from dotenv import load_dotenv
import os
import telebot
from db_driver import db
from config import buttons, misc
from tools import serialize_game_list, serialize_game


BASE_DIR = os.path.dirname(__file__) # project/
ENV_PATH = os.path.join(BASE_DIR, "config", ".env")

load_dotenv(ENV_PATH)

TOKEN = os.getenv("TG_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS").split(',')))
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    # New user start logging
    # main_logger.info(f"Start chat with user: {message.from_user.first_name} ({message.from_user.id})")

    bot.send_message(
        message.chat.id,
        "Welcome to SecretSanta game",
        reply_markup=keyboards.get_main_interface_keyboard(message=message, ids=ADMIN_IDS)
    )


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == buttons.NEW_GAME_BUTTON:
        new_game_str = db.new_game(game_name=misc.BASE_GAME_NAME)
        bot.send_message(message.chat.id, f"New game created: {new_game_str}")
    elif message.text == buttons.LIST_GAMES_BUTTON:
        all_games = db.get_all_games()
        all_games_str = serialize_game_list(all_games)
        bot.send_message(message.chat.id, f"GAMES LIST:\n\n{all_games_str}")
    elif message.text == buttons.JOIN_GAME_BUTTON:
        bot.send_message(message.chat.id, f"Enter game ID for join:")
        bot.register_next_step_handler(message, choice_game)
    elif message.text == buttons.LOCK_GAME_BUTTON:
        bot.send_message(message.chat.id, f"Enter game ID for locking: ")
        bot.register_next_step_handler(message, lock_game)
    elif message.text == buttons.GET_GAME_DATA_BUTTON:
        bot.send_message(message.chat.id, f"Enter game ID for display game data:")
        bot.register_next_step_handler(message, get_game_data)


def choice_game(message):
    game = db.get_game(message.text)
    if game["status"]:
        game_name = message.text
        msg = "Enter your full name"
        bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(message, join_game, game_name)
    else:
        bot.send_message(
            message.chat.id,
            game["message"],
            reply_markup=keyboards.get_main_interface_keyboard(message=message, ids=ADMIN_IDS)
        )
        bot.register_next_step_handler(message, handle_message)


def join_game(message, game_name=None):
    game_name = game_name
    player_name = message.text
    player_telegram_id = message.chat.id
    result = db.join_game_by_name(game_name=game_name, player_name=player_name, player_telegram_id=player_telegram_id)
    bot.send_message(
        message.chat.id,
        result,
        reply_markup=keyboards.get_main_interface_keyboard(message=message, ids=ADMIN_IDS)
    )
    bot.register_next_step_handler(message, handle_message)


def lock_game(message):
    result = db.lock_game_by_name(message.text)
    bot.send_message(
        message.chat.id,
        result,
        reply_markup=keyboards.get_main_interface_keyboard(message=message, ids=ADMIN_IDS)
    )
    bot.register_next_step_handler(message, handle_message)


def get_game_data(message):
    result = db.get_players_by_game_name(message.text)
    output_msg = serialize_game(result)
    bot.send_message(
        message.chat.id,
        output_msg,
        reply_markup=keyboards.get_main_interface_keyboard(message=message, ids=ADMIN_IDS)
    )
    bot.register_next_step_handler(message, handle_message)


def run_game_by_name(message):
    result = db.get_players_by_game_name(message.text)
    output_msg = serialize_game(result)


if __name__ == '__main__':
    bot.infinity_polling()