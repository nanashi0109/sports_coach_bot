import datetime
import sqlite3

from src.tools.bot_message import BotMessage


class Goal:
    def __init__(self, goal_header: str,
                 type_activity: str,
                 deadline: datetime.date,
                 target_stat: float,
                 current_stat: float = 0,
                 description: str = None,
                 is_completed: bool = False,
                 id_sql: int = None):
        self.__goal_header = goal_header
        self.__type_activity = type_activity
        self.__target_stat = target_stat
        self.__current_stat = current_stat
        self.__deadline = deadline
        self.__description = description
        self.__is_completed = is_completed

        self.__id_sql = id_sql

    def __str__(self):
        value = self.__current_stat if self.__target_stat >= self.__current_stat else self.__target_stat

        result = (f"Тип тренировки: {self.__type_activity}\n"
                  f"Цель: {self.__goal_header}\n"
                  f"Прогресс: {value}/{self.target_stat}\n")

        if self.__is_completed:
            result = "-----Выполнено-----\n" + result
        else:
            result += f"Дней осталось: {(self.__deadline - datetime.date.today()).days}\n"

        if self.__description is not None:
            result += f"Описание: {self.__description}"

        return result

    @property
    def goal_header(self):
        return self.__goal_header

    @property
    def type_activity(self):
        return self.__type_activity

    @property
    def deadline(self):
        return self.__deadline

    @property
    def target_stat(self):
        return self.__target_stat

    @property
    def current_stat(self):
        return self.__current_stat

    @property
    def description(self):
        return self.__description

    @property
    def is_completed(self):
        return self.__is_completed

    @property
    def id_sql(self):
        return self.__id_sql


class GoalsSql:
    def __init__(self):
        self.__connection = sqlite3.connect("sport_coach.dp")
        self.__cursor = self.__connection.cursor()
        self.__create_dp()

    def __create_dp(self):
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS Goals(
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            goal_header     TEXT NOT NULL,
            type_activity   TEXT NOT NULL,
            deadline        DATETIME NOT NULL,
            target_stat     FLOAT,
            current_stat    FLOAT,
            description     TEXT,
            is_completed    BOOL
            );
        """)

    def add_goal(self, chat_id: int, goal: Goal):
        self.__cursor.execute("""
        INSERT INTO Goals (user_id, goal_header, type_activity, deadline, target_stat, current_stat, description, is_completed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (chat_id, goal.goal_header, goal.type_activity, goal.deadline, goal.target_stat,
              goal.current_stat, goal.description, goal.is_completed))

        self.__connection.commit()

    def get_all_goals_by_user_id(self, user_id) -> list or None:
        self.__cursor.execute("""
        SELECT id, goal_header, type_activity, deadline, target_stat, current_stat, description, is_completed FROM Goals 
        WHERE "user_id" = ?;
        """, (user_id, ))

        goals_tuples = self.__cursor.fetchall()

        if goals_tuples is None:
            return None

        return self.convert_tuple_into_list_goals(goals_tuples)

    def remove_goal(self, goal):
        self.__cursor.execute("""DELETE FROM Goals WHERE id = ?""", (goal.id_sql, ))

        self.__connection.commit()

    def convert_tuple_into_list_goals(self, workout_tuples) -> list:
        goals = []

        for (id_sql, goal_header, type_activity, deadline, target_stat, current_stat, description, is_completed) in workout_tuples:
            goal = Goal(goal_header=goal_header, type_activity=type_activity,
                        deadline=datetime.datetime.strptime(deadline, '%Y-%m-%d').date(),
                        target_stat=int(target_stat), current_stat=int(current_stat), description=description,
                        is_completed=bool(is_completed), id_sql=id_sql)
            goals.append(goal)

        return goals

    def update_goal_states(self, user_id: int, type_activity: str, value: float):
        self.__cursor.execute("UPDATE Goals SET current_stat = current_stat + ? "
                              "WHERE type_activity = ? AND user_id = ?;",
                              (value, type_activity, user_id))

        self.__check_goals_on_complete(user_id)

        self.__connection.commit()

    def __check_goals_on_complete(self, user_id: int):
        goals = self.get_all_goals_by_user_id(user_id)

        for goal in goals:
            if not goal.is_completed and goal.target_stat <= goal.current_stat:
                BotMessage.send_message(user_id, "Цель достигнута!")

        self.__cursor.execute("""
        UPDATE Goals SET is_completed = True 
        WHERE current_stat >= target_stat AND user_id = ?;""",
                              (user_id, ))
