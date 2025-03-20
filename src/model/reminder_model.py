import datetime
from dateutil.relativedelta import relativedelta
from enum import IntEnum

import sqlite3
from src.tools.bot_message import BotMessage
from src.tools.time_waiter import Waiter

from resources.constants import TYPES_REPEATING_REMINDER


class ReminderRepeating(IntEnum):
    NOT_REPEAT = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3


class ReminderType(IntEnum):
    WORKOUT = 1,
    GOAL = 2,
    RECORD = 3
    USER_WORKOUT = 4


class ReminderModel:
    def __init__(self, time_remind: datetime,
                 type: ReminderType = ReminderType.USER_WORKOUT,
                 repeating: ReminderRepeating = ReminderRepeating.NOT_REPEAT,
                 description: str = None, id: int = None, user_id: int = None):
        self.__time_remind = time_remind
        self.__type = type
        self.__repeating = repeating
        self.__description = description
        self.__id = id
        self.__user_id = user_id

    def __str__(self):
        result = (f"Напоминание #{self.id}\n"
                  f"Дата и время: {self.__time_remind}\n"
                  f"Повторение: {TYPES_REPEATING_REMINDER[self.__repeating]}\n")

        return result

    @property
    def time_remind(self) -> datetime:
        return self.__time_remind

    @time_remind.setter
    def time_remind(self, value) -> None:
        self.__time_remind = value

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
    def id(self, value) -> None:
        self.__id = value

    @property
    def user_id(self):
        return self.__user_id


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

    def remove_by_id_and_user_id(self, id: int, user_id: int):
        self.__cursor.execute("""DELETE FROM reminders WHERE id = ? AND user_id = ?""", (id, user_id))

        self.__connection.commit()

    def update_remind_time(self, id: int, new_time: datetime.datetime):
        self.__cursor.execute("""UPDATE reminders SET time = ? WHERE id = ?""",
                              (new_time, id))

        self.__connection.commit()

    def get_all_by_user_id(self, user_id: int):
        self.__cursor.execute("""
        SELECT id, user_id, time, type, repeating, description FROM reminders WHERE user_id = ?;
        """, (user_id, ))

        reminders = self.__convert_to_list(self.__cursor.fetchall())

        return reminders

    def get_all_user_reminder_by_user_id(self, user_id: int):
        self.__cursor.execute("""
        SELECT id, user_id, time, type, repeating, description FROM reminders 
        WHERE user_id = ? and type = 4; 
        """, (user_id, ))

        reminders = self.__convert_to_list(self.__cursor.fetchall())

        return reminders

    def get_all(self):
        self.__cursor.execute("""
        SELECT id, user_id, time, type, repeating, description FROM reminders;
        """)

        reminders = self.__convert_to_list(self.__cursor.fetchall())

        return reminders

    def __convert_to_list(self, reminder_tuple):
        reminders = []

        for (id, user_id, time, type, repeating, description) in reminder_tuple:
            reminder = ReminderModel(id=id, time_remind=datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S'),
                                     type=ReminderType(type), repeating=ReminderRepeating(repeating),
                                     description=description, user_id=user_id)
            reminders.append(reminder)

        return reminders


class ReminderController:
    @staticmethod
    def create_reminder(user_id: int,
                        date: datetime, type: ReminderType,
                        repeat: ReminderRepeating, description: str = None):
        from src.model.databases import reminder_dp

        reminder = ReminderModel(date, type, repeat, description)

        reminder_dp.add(user_id, reminder)

        Waiter.add_time_to_wait(date, ReminderController.on_active_reminder, user_id, reminder)

    @staticmethod
    def add_reminder(user_id: int, reminder: ReminderModel):
        from src.model.databases import reminder_dp

        reminder_dp.add(user_id, reminder)
        reminder.id = ReminderController.get_last_id()

        Waiter.add_time_to_wait(reminder.time_remind, ReminderController.on_active_reminder, user_id, reminder)

    @staticmethod
    def update_remind(user_id: int, remind: ReminderModel):
        from src.model.databases import reminder_dp

        reminder_dp.update_remind_time(remind.id, remind.time_remind)
        Waiter.add_time_to_wait(remind.time_remind, ReminderController.on_active_reminder, user_id, remind)

    @staticmethod
    def on_active_reminder(user_id: int, reminder: ReminderModel):
        from src.model.databases import reminder_dp
        BotMessage.send_message(user_id, reminder.description)

        match reminder.repeating:
            case ReminderRepeating.DAILY:
                reminder.time_remind += datetime.timedelta(days=1)
            case ReminderRepeating.WEEKLY:
                reminder.time_remind += datetime.timedelta(days=7)
            case ReminderRepeating.MONTHLY:
                reminder.time_remind += relativedelta(months=1)
            case ReminderRepeating.NOT_REPEAT:
                reminder_dp.remove_by_id(reminder.id)
                return

        ReminderController.update_remind(user_id, reminder)

    @staticmethod
    def add_all_reminder_from_db():
        from src.model.databases import reminder_dp

        reminders = reminder_dp.get_all()

        for reminder in reminders:
            Waiter.add_time_to_wait(reminder.time_remind,
                                    ReminderController.on_active_reminder, reminder.user_id, reminder)

    @staticmethod
    def get_last_id():
        from src.model.databases import reminder_dp

        ids = [remind.id for remind in reminder_dp.get_all()]

        if len(ids) == 0:
            return 0

        return max(ids)
