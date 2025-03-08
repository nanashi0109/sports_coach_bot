import datetime
import asyncio


class Waiter:
    def __init__(self):
        self.__callback_for_waiting = []

    def add_time_to_wait(self, target: datetime.datetime, callback, *args):
        self.__callback_for_waiting.append([target, callback, args])

    def remove_time_to_wait(self, target: datetime.datetime):
        self.__callback_for_waiting.remove(target)

    async def wait(self):
        while True:
            now = datetime.datetime.now()

            nearest_time = self.get_nearest_date()

            print(nearest_time)
            if nearest_time is not None and now >= nearest_time[1]:
                print(f"Waiter {nearest_time}")
                parameter = self.__callback_for_waiting[nearest_time[0]]

                parameter[1](*parameter[2])

            await asyncio.sleep(1)

    def get_nearest_date(self) -> tuple:
        now = datetime.datetime.now()

        times_list = []

        for data in self.__callback_for_waiting:
            times_list.append(data[0])

        index = 0
        nearest_datetime = None
        min_diff = None

        for i in range(0, len(times_list), 1):
            diff = (times_list[i] - now).total_seconds()

            if min_diff is None or diff < min_diff:
                min_diff = diff
                nearest_datetime = times_list[i]
                index = i

        return index, nearest_datetime
