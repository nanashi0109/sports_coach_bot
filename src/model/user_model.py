import sqlite3


class User:
    def __init__(self, login: str, password: str, chat_id: int, id_user: int = None, ):
        self.__id = id_user
        self.__chat_id = chat_id
        self.__login = login
        self.__password = password

    @property
    def login(self):
        return self.__login

    @property
    def password(self):
        return self.__password

    @property
    def chat_id(self):
        return self.__chat_id


class UsersSql:
    def __init__(self):
        self.__connection = sqlite3.connect("sport_coach.dp")
        self.__cursor = self.__connection.cursor()
        self.__create_dp()

    def __create_dp(self):
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users(
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id     INTEGER NOT NULL,
            login       TEXT NOT NULL,
            password    TEXT NOT NULL
            );
        """)

    def add_user(self, user: User) -> None:
        chat_id = user.chat_id
        login = user.login
        password = user.password

        self.__cursor.execute("""
            INSERT INTO Users(chat_id, login, password)
            VALUES (?, ?, ?) """, (chat_id, login, password))

        self.__connection.commit()

    def get_user_by_login(self, target_login) -> User or None:
        self.__cursor.execute(f"""
            SELECT * FROM Users WHERE "{target_login}" = login;
        """)

        result = self.__cursor.fetchone()
        if result is None:
            print("Login not found")
            return None

        user = User(result[2], result[3], result[1], id_user=result[0])
        return user

    def get_user_by_chat_id(self, chat_id) -> User or None:
        self.__cursor.execute(f"""
            SELECT * FROM Users WHERE "{chat_id}" = chat_id;
        """)

        result = self.__cursor.fetchone()
        if result is None:
            return None

        user = User(result[2], result[3], id_user=result[0], chat_id=result[1])
        return user

    def get_all_logins(self) -> list:
        self.__cursor.execute("""
            SELECT login FROM Users;
            """)

        result = self.__cursor.fetchall()
        logins = []
        for login in result:
            logins.append(login[0])

        return logins

