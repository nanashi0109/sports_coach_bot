from src.model.databases import workout_dp
import datetime


class Statistics:

    @staticmethod
    def get_summary_distance(user_id, type_activity=None, count_days=None):
        workouts = Statistics.get_filter_workouts(user_id, type_activity, count_days)

        workouts = list(filter(lambda workout: workout.distance is not None, workouts))

        return sum([workout.distance for workout in workouts])

    @staticmethod
    def get_avg_distance(user_id, type_activity=None, count_days=None):
        workouts = Statistics.get_filter_workouts(user_id, type_activity, count_days)

        workouts = list(filter(lambda workout: workout.distance is not None, workouts))

        if len(workouts) == 0:
            return 0

        avg_distance = sum([workout.distance for workout in workouts]) / len(workouts)

        return avg_distance

    @staticmethod
    def get_summary_duration_training(user_id, type_activity=None, count_days=None):
        workouts = Statistics.get_filter_workouts(user_id, type_activity, count_days)

        workouts = list(filter(lambda workout: workout.distance is not None, workouts))

        durations = [workout.duration for workout in workouts]

        summary_time = datetime.timedelta()
        for time in durations:
            summary_time += datetime.timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)

        return str(summary_time)

    @staticmethod
    def get_avg_duration_training(user_id, type_activity=None, count_days=None):
        workouts = Statistics.get_filter_workouts(user_id, type_activity, count_days)

        workouts = list(filter(lambda workout: workout.distance is not None, workouts))

        if len(workouts) == 0:
            return 0

        durations = [workout.duration for workout in workouts]

        summary_time = datetime.timedelta()
        for time in durations:
            summary_time += datetime.timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)

        return str(summary_time / len(workouts))

    @staticmethod
    def get_summary_calories_training(user_id, type_activity=None, count_days=None):
        workouts = Statistics.get_filter_workouts(user_id, type_activity, count_days)

        workouts = list(filter(lambda workout: workout.calories is not None, workouts))

        return sum([workout.calories for workout in workouts])

    @staticmethod
    def get_avg_calories(user_id, type_activity=None, count_days=None):
        workouts = Statistics.get_filter_workouts(user_id, type_activity, count_days)

        workouts = list(filter(lambda workout: workout.calories is not None, workouts))

        if len(workouts) == 0:
            return 0

        avg_calories = sum([workout.calories for workout in workouts]) / len(workouts)

        return avg_calories

    @staticmethod
    def get_count_training(user_id, type_activity=None, count_days=None):
        workouts = Statistics.get_filter_workouts(user_id, type_activity, count_days)
        return len(workouts)

    @staticmethod
    def get_filter_workouts(user_id, type_activity=None, count_days=None):
        workouts = workout_dp.get_all_workouts_by_user_id(user_id)

        if type_activity is not None:
            workouts = workout_dp.sort_workouts_by_type(workouts, type_activity)
        if count_days is not None:
            workouts = workout_dp.sort_workouts_by_period_of_time(workouts, count_days)

        return workouts
