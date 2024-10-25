from models import User


def get_user_by_id_sql(user_id):
    return f"SELECT * FROM USERS WHERE id={user_id}"


def get_users_sql():
    return "SELECT * FROM USERS"


def create_user_sql(user_id, username, email, is_admin):
    return f'INSERT INTO USERS VALUES ({user_id}, "{username}", "{email}", {is_admin})'


def update_user_sql(user_id, user: User):
    return f'UPDATE USERS SET username="{user.username}", email="{user.email}" WHERE id={user_id}'
