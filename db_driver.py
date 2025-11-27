import sqlite3
from typing import List


class SQLiteDatabaseConnection:
    def __init__(self, database_name: str):
        self.database_name = database_name
        self.create_check_table()


    def execute_query(self, query: str, params=None):
        """Execute a SQL query with optional parameters and return results if available."""
        try:
            with sqlite3.connect(self.database_name) as db_conn:
                db_conn.execute("PRAGMA foreign_keys = ON;")
                cursor = db_conn.cursor()
                if params is not None:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                db_conn.commit()

                if cursor.description:
                    return cursor.fetchall()
                return cursor.lastrowid

        except sqlite3.DatabaseError as e:
            # logger.error(e)
            raise


    def create_check_table(self):
        """Create the products table if it does not exist."""

        query = """
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            game_name TEXT NOT NULL UNIQUE,
            game_locked INTEGER DEFAULT 0,
            game_completed INTEGER DEFAULT 0
         );
        """
        self.execute_query(query)

        query = """
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            player_name TEXT NOT NULL,
            player_telegram_id INTEGER NOT NULL,
            player_giver TEXT DEFAULT NULL,
            player_receiver TEXT DEFAULT NULL,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
            UNIQUE (game_id, player_name),
            UNIQUE (game_id, player_telegram_id)
         );
        """
        self.execute_query(query)


    def new_game(self, game_name: str):
        # Create new instance (new game) in 'games' table
        query = """
        INSERT INTO games (game_name)
        VALUES (:game_name);
        """

        params = {"game_name": game_name}
        new_game_id = self.execute_query(query, params)

        # Update record (with following 'new_game_id') with 'new_game_name'
        new_game_name = f"{game_name}_{new_game_id}"
        update_query = """
        UPDATE games
        SET game_name = :new_game_name
        WHERE id = :new_game_id;
        """

        update_params = {"new_game_name": new_game_name, "new_game_id": new_game_id}
        self.execute_query(update_query, update_params)

        return new_game_name


    def get_all_games(self) -> List[tuple]:
        query = """
        SELECT games.*, COUNT(players.player_id) AS players_count
        FROM games
        LEFT JOIN players ON games.id = players.game_id
        GROUP BY games.id;
        """

        result = self.execute_query(query)
        return result


    def get_game(self, game_name: str) -> dict:
        query = """
        SELECT *
        FROM games
        WHERE game_name = :game_name
        """

        result = self.execute_query(query, {"game_name": game_name})

        if not result:
            return {"status": False, "message": f"Game: {game_name} not found", "result": None}
        elif result[0][3]:
            return {"status": False, "message": f"Game: {game_name} already locked", "result": result[0]}
        elif result[0][4]:
            return {"status": False, "message": f"Game: {game_name} already completed", "result": result[0]}

        return {"status": True, "message": "Successful", "result": result[0]}


    def lock_game_by_name(self, game_name: str) -> str:
        game = self.get_game(game_name)

        if not game["status"]:
            return game["message"]

        query = """
        UPDATE games
        SET game_locked = 1
        WHERE game_name = :game_name;
        """

        update_params = {"game_name": game_name}
        self.execute_query(query, update_params)

        return f"Game: {game_name} has been locked"


    def join_game_by_name(self, game_name: str, player_name: str, player_telegram_id: int) -> str:
        game = self.get_game(game_name)
        if not game["status"]:
            return game["message"]

        game_id = game["result"][0]

        try:
            query = """
            INSERT INTO players (game_id, player_name, player_telegram_id)
            VALUES (:game_id, :player_name, :player_telegram_id)
            """

            insert_params = {
                "game_id": game_id,
                "player_name": player_name,
                "player_telegram_id": player_telegram_id
            }

            self.execute_query(query, insert_params)
            return f"Player: {player_name} joined game: {game_name}"

        except sqlite3.IntegrityError as e:
            return f"You can join a game: {game_name} only once"


    #
    # def get_record(self, day: str = ''):
    #     with sqlite3.connect(self.database_name) as connection:
    #         cursor = connection.cursor()
    #
    #         query = """
    #                 SELECT schedule.number_of_lesson, \
    #                        schedule.start_time, \
    #                        schedule.end_time, \
    #                        schedule.name_of_lesson, \
    #                        schedule.day_of_week \
    #                 FROM schedule \
    #                          INNER JOIN week ON week.day_of_week = schedule.day_of_week
    #                 WHERE week.day_of_week LIKE :day \
    #                 """
    #         result = cursor.execute(query, {"day": day}).fetchall()
    #         return result
    #
    # def get_all_records(self):
    #     with sqlite3.connect(self.database_name) as connection:
    #         cursor = connection.cursor()
    #
    #         query = """
    #                 SELECT schedule.number_of_lesson, \
    #                        schedule.start_time, \
    #                        schedule.end_time, \
    #                        schedule.name_of_lesson, \
    #                        schedule.day_of_week \
    #                 FROM schedule \
    #                 """
    #
    #         result = cursor.execute(query).fetchall()
    #         return result
    #
    # def edit_record(self, *, day: str, lesson: int, name_of_lesson: str):
    #     with sqlite3.connect(self.database_name) as connection:
    #         cursor = connection.cursor()
    #
    #         query = """
    #                 UPDATE schedule
    #                 SET name_of_lesson = :name_of_lesson
    #                 WHERE schedule.day_of_week = :day \
    #                   AND schedule.number_of_lesson = :lesson \
    #                 """
    #         cursor.execute(query, {"day": day, "lesson": lesson, "name_of_lesson": name_of_lesson})
    #
    # def add_record(self, *, day: str, lesson: int, name_of_lesson: str):
    #     with sqlite3.connect(self.database_name) as connection:
    #         cursor = connection.cursor()
    #         values = [day, lesson, TEMP_TIME_LIST[0], TEMP_TIME_LIST[1], name_of_lesson]
    #         query = """
    #                 INSERT INTO schedule(day_of_week, number_of_lesson, start_time, end_time, name_of_lesson)
    #                 VALUES (?, ?, ?, ?, ?) \
    #                 """
    #         cursor.execute(query, values)
    #         connection.commit()
    #
    # def delete_record(self, *, day: str, lesson: int):
    #     with sqlite3.connect(self.database_name) as connection:
    #         cursor = connection.cursor()
    #         query = """
    #                 DELETE \
    #                 FROM schedule
    #                 WHERE day_of_week = :day \
    #                   AND number_of_lesson = :lesson \
    #                 """
    #         cursor.execute(query, {"day": day, "lesson": lesson})
    #         connection.commit()

db = SQLiteDatabaseConnection('santa.sqlite3')