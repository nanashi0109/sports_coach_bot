HELLO_MESSAGE = ("Привет! Это Telegram-бот, который поможет тебе фиксировать свою спортивную активность, "
                 "отслеживать динамику тренировок и прогресс, а также достигать поставленных целей в спорте. "
                 "Бот может предоставить статистику по различным видам активности (бег, ходьба, плавание и т.д.), "
                 "а также поддерживает установку целей и напоминаний о необходимости регулярно заниматься спортом.")

HELP_MESSAGE = ("Список команд\n"
                "/register - регистрация, если нет аккаунта\n"
                "/login - вход в уже существующий аккаунт\n"
                "/add_workout - добавление новой тренировки\n"
                "/view_workouts - просмотор истории тренировок\n"
                "/set_goal - установка цели\n"
                "/view_goals - просмотр всех текущих целей\n"
                "/statistics - просмотр статистики и аналитики\n"
                "/set_reminder - установить напоминаний")

NEED_REGISTRY_TEXT = "Для начала нужно зарегистрироваться  с помощью команды /register"
WORKOUT_REMINDER_TEXT = "У вас запланирована тренировка!"


DATETIME_FORMAT = '%Y:%m:%d:%H:%M'

TYPES_ACTIVITIES = ["Бег", "Ходьба", "Плавание"]
GOALS_FOR_TYPES_ACTIVITIES = {
    "Бег": ["Пробежать n км"],
    "Ходьба": ["Пройти n км"],
    "Плавание": ["Проплыть n км"],
}

TYPES_REPEATING_REMINDER = ["Не повторять", "Ежедневно", "Еженедельно", "Ежемесячно"]
