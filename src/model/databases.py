import sqlite3


class User:
    def __init__(self, login, password, id_user: int = None):
        self.__id = id_user
        self.__login = login
        self.__password = password

    @property
    def login(self):
        return self.__login

    @property
    def password(self):
        return self.__password


class UsersSql:
    def __init__(self):
        self.__connection = sqlite3.connect("sport_coach.dp")
        self.__cursor = self.__connection.cursor()
        self.__create_dp()

    def __create_dp(self):
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users(
            id  INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT NOT NULL,
            password TEXT NOT NULL
            );
        """)

    def add_user(self, user: User):
        login = user.login
        password = user.password

        self.__cursor.execute("""
            INSERT INTO Users(login, password)
            VALUES (?, ?) """, (login, password))

    def get_user_by_login(self, target_login):
        self.__cursor.execute(f"""
            SELECT * FROM Users WHERE "{target_login} = login"
        """)

        result = self.__cursor.fetchone()

        user = User(result[1], result[2], id_user=result[0])
        return user

