from src.model import user_model, workout_model, goal_model


user_dp = user_model.UsersSql()

workout_dp = workout_model.WorkoutsSql()

goals_dp = goal_model.GoalsSql()
