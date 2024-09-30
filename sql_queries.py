from user_types import User


def getUserByIdSQL(userId):
    return f"SELECT * FROM USERS WHERE id={userId};"


def getUsersSQL():
    return "SELECT * FROM USERS;"


def createUserSQL(id, username, email, isAdmin):
    return f'INSERT INTO USERS VALUES ({id}, "{username}", "", "{email}", {isAdmin});'


def updateUserSQL(userId, user: User):
    return f'UPDATE USERS SET username="{user.username}", email="{user.email}" WHERE id={userId};'
