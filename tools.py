from typing import List


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