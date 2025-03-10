from datetime import datetime
from enum import IntEnum

import sqlite3
from src.tools.bot_message import BotMessage
from src.tools.time_waiter import Waiter


class ReminderRepeating(IntEnum):
    NOT_REPEAT = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3


class ReminderType(IntEnum):
    WORKOUT = 1,
    GOAL = 2,
    RECORD = 3


class ReminderController:
    @staticmethod
    def create_reminder(user_id: int,
                        date: datetime, type: ReminderType,
                        repeat: ReminderRepeating, description: str = None):
        from src.model.databases import reminder_dp

        reminder = ReminderModel(date, type, repeat, description)

        reminder_dp.add(user_id, reminder)

        Waiter.add_time_to_wait(date, BotMessage.send_message, user_id, description)


class ReminderModel:
    def __init__(self, time_remind: datetime,
                 type: ReminderType,
                 repeating: ReminderRepeating = ReminderRepeating.NOT_REPEAT,
                 description: str = None, id: int = None):
        self.__time_remind = time_remind
        self.__type = type
        self.__repeating = repeating
        self.__description = description
        self.__id = id

    def __str__(self):
        pass

    @property
    def time_remind(self) -> datetime:
        return self.__time_remind

    @property
    def type(self) -> ReminderType:
        return self.__type

    @property
    def repeating(self) -> ReminderRepeating:
        return self.__repeating

    @property
    def description(self) -> str:
        return self.__description

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, value: int):
        self.__id = value


class ReminderDB:
    def __init__(self):
        self.__connection = sqlite3.connect("sport_coach.dp")
        self.__cursor = self.__connection.cursor()
        self.__create_db()

    def __create_db(self):
        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS reminders(
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            time        DATETIME NOT NULL,
            type        INTEGER NOT NULL,
            repeating   INTEGER NOT NULL,
            description TEXT
        );""")

    def add(self, user_id: int, reminder: ReminderModel):
        self.__cursor.execute("""INSERT INTO reminders(user_id, time, type, repeating, description) 
        VALUES(?, ?, ?, ?, ?);""",
                              (user_id, reminder.time_remind, int(reminder.type),
                               int(reminder.repeating), reminder.description))

        self.__connection.commit()

    def remove_by_id(self, id: int):
        self.__cursor.execute("""DELETE FROM reminders WHERE id = ?""", (id, ))

        self.__connection.commit()

    def get_all_by_user_id(self, user_id: int):
        self.__cursor.execute("""
        SELECT (id, time, type, repeating, description) FROM reminders WHERE user_id = ?;
        """, (user_id, ))

        reminders = self.__convert_to_list(self.__cursor.fetchall())

        return reminders

    def get_all(self):
        self.__cursor.execute("""
        SELECT (id, time, type, repeating, description) FROM reminders;
        """)

        reminders = self.__convert_to_list(self.__cursor.fetchall())

        return reminders

    def __convert_to_list(self, reminder_tuple):
        reminders = []

        for (id, time, type, repeating, description) in reminder_tuple:
            reminder = ReminderModel(id=id, time_remind=datetime.strptime(time, '%Y-%m-%d %H:%M:%S'),
                                     type=ReminderType(type), repeating=ReminderRepeating(repeating),
                                     description=description)
            reminders.append(reminder)

        return reminders
