import datetime
import sqlite3


class Workout:
    def __init__(self,
                 type_activity: str,
                 date_activity: datetime.datetime,
                 duration: datetime.time = None,
                 distance: float = None,
                 calories: int = None,
                 description: str = None):
        self.__type_activity = type_activity
        self.__date = date_activity

        self.__duration = duration
        self.__distance = distance
        self.__calories = calories
        self.__description = description

    def __str__(self):
        result = ""
        result += f"Тип тренировки: {self.type_activity}\n"

        if self.distance is not None:
            result += f"Дистанция: {self.distance}\n"
        result += f"Дата: {self.date_activity}\nПродолжительность: {self.duration}\n"

        if self.calories is not None:
            result += f"Кол-во калорий: {self.calories}\n"

        if self.description is not None:
            result += f"Описание: {self.description}"

        return result

    @property
    def type_activity(self) -> str:
        return self.__type_activity

    @property
    def date_activity(self) -> datetime.datetime:
        return self.__date

    @property
    def duration(self) -> datetime.time:
        return self.__duration

    @property
    def distance(self) -> float:
        return self.__distance

    @property
    def calories(self) -> int:
        return self.__calories

    @property
    def description(self) -> str:
        return self.__description


class WorkoutsSql:
    def __init__(self):
        self.__connection = sqlite3.connect("sport_coach.dp")
        self.__cursor = self.__connection.cursor()
        self.__create_dp()

    def __create_dp(self):
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS Workouts(
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            type_activity   TEXT NOT NULL,
            date_activity   DATETIME NOT NULL,
            duration        TIME,
            distance        FLOAT,
            calories        INTEGER,
            description     TEXT
            );
        """)

    def add_workout(self, chat_id: int, workout: Workout) -> None:
        self.__cursor.execute("""
        INSERT INTO Workouts (user_id, type_activity, date_activity, duration, distance, calories, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (chat_id, workout.type_activity,
              workout.date_activity, str(workout.duration),
              workout.distance, workout.calories,
              workout.description))

        self.__connection.commit()

    def get_all_workouts_by_user_id(self, user_id) -> list or None:
        self.__cursor.execute("""
        SELECT type_activity, date_activity, duration, distance, calories, description FROM Workouts 
        WHERE "user_id" = ?;
        """, (user_id, ))

        workout_tuples = self.__cursor.fetchall()

        if workout_tuples is None:
            return None

        return self.convert_tuple_into_list_workout(workout_tuples)

    def get_all_workouts_by_period_of_time(self, user_id: int, period) -> list:
        today = datetime.date.today()
        last_day = today - datetime.timedelta(days=period)

        self.__cursor.execute("""
            SELECT type_activity, date_activity, duration, distance, calories, description FROM Workouts 
            WHERE "user_id" = ? AND "date_activity" >= ? AND "date_activity" <= ?;
        """, (user_id, last_day, today))

        workouts_tuples = self.__cursor.fetchall()

        return self.convert_tuple_into_list_workout(workouts_tuples)

    def get_all_workouts_by_type(self, user_id: int, type_activity) -> list:
        self.__cursor.execute("""
            SELECT type_activity, date_activity, duration, distance, calories, description FROM Workouts 
            WHERE "user_id" = ? AND "type_activity" = ?;
        """, (user_id, type_activity))

        workouts = self.__cursor.fetchall()

        return self.convert_tuple_into_list_workout(workouts)

    def sort_workouts_by_period_of_time(self, workouts, period) -> list:
        today = datetime.date.today()
        last_day = today - datetime.timedelta(days=period)

        result_workouts = []

        for workout in workouts:
            if (workout.date_activity >= last_day) and (workout.date_activity <= today):
                result_workouts.append(workout)

        return result_workouts

    def sort_workouts_by_type(self, workouts, type_activity) -> list:
        result_workouts = []

        for workout in workouts:
            if workout.type_activity == type_activity:
                result_workouts.append(workout)

        return result_workouts

    def convert_tuple_into_list_workout(self, workout_tuples) -> list:
        workouts = []

        for (type_activity, date_activity, duration, distance, calories, description) in workout_tuples:
            workout = Workout(type_activity, date_activity, duration=duration, distance=distance,
                              calories=calories, description=description)
            workouts.append(workout)

        return workouts
