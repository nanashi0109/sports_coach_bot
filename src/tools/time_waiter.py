import datetime
import asyncio


class Waiter:
    __callback_for_waiting = []

    @classmethod
    def recover_waiting(cls):
        from src.model.databases import workout_dp, goals_dp
        from src.model.reminder_model import ReminderController

        print("Start recovering...")

        workouts = workout_dp.get_all_after_now()
        for workout in workouts:
            time_delta = datetime.timedelta(hours=workout.duration.hour,
                                            minutes=workout.duration.minute,
                                            seconds=workout.duration.second)
            date_ending = workout.date_activity + time_delta
            cls.add_time_to_wait(date_ending, goals_dp.update_goal_states,  workout.user_id, workout.type_activity, workout.distance)

        ReminderController.add_all_reminder_from_db()

        print(f"End recovering. Recover {len(cls.__callback_for_waiting)} count")

    @classmethod
    def add_time_to_wait(cls, target: datetime.datetime, callback, *args):
        cls.__callback_for_waiting.append([target, callback, args])
        print(f"Add callback to wait: {target}")

    @classmethod
    def remove_time_to_wait(cls, index: int):
        cls.__callback_for_waiting.pop(index)

    @classmethod
    async def wait(cls):
        print("Start waiter")
        while True:
            now = datetime.datetime.now()

            nearest_time = cls.get_nearest_date()

            if nearest_time[1] is not None:
                if now >= nearest_time[1]:
                    print(f"We waited: {nearest_time[1]}")
                    parameter = cls.__callback_for_waiting[nearest_time[0]]

                    parameter[1](*parameter[2])

                    cls.remove_time_to_wait(nearest_time[0])

            await asyncio.sleep(1)

    @classmethod
    def get_nearest_date(cls) -> tuple:
        times_list = []

        for data in cls.__callback_for_waiting:
            times_list.append(data[0])

        if len(times_list) == 0:
            print("List is empty")
            return 0, None

        nearest_datetime = min(times_list)
        min_index = times_list.index(nearest_datetime)

        return min_index, nearest_datetime
