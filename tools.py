from typing import List, Tuple, Union


def serialize_game_list(game_list: List[tuple]):
    final_row = ""
    for game_data in game_list:
        if not game_data[3] and not game_data[4]:
            game_status = "Open"
        elif game_data[3] and not game_data[4]:
            game_status = "Closed"
        else:
            game_status = "Completed"

        game_date = game_data[1].split()[0]
        game_name = game_data[2]
        players_qty = game_data[5]

        final_row += f"Date: {game_date} | ID: {game_name} | Players: {players_qty} | Status: {game_status}\n"

    if not game_list:
        final_row = "No games found"

    return final_row

def serialize_game(game_result: Union[dict, str]):
    if isinstance(game_result, str):
        return game_result

    game_data = game_result["game"]
    players_data = game_result["players"]
    locked = "Yes" if game_data[3] else "No"
    completed = "Yes" if game_data[4] else "No"

    msg = (
        f"Game: {game_data[2]}\n\n"
        f"Created: {game_data[1]}\n"
        f"Locked: {locked}\n"
        f"Completed: {completed}\n\n"
        f"Players:\n"
    )

    for number, player in enumerate(players_data, start=1):

        receiver = player[2] if player[2] else "None"
        msg += f"{number}. {player[1]} -> gives to: {receiver}\n"

    return msg
