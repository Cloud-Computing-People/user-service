from models import User


def get_user_by_id_sql(user_id):
    return f"SELECT * FROM USERS WHERE id={user_id};"

def get_user_player_by_id_sql(user_id):
    return f"SELECT * FROM USERS, PLAYER_DATA WHERE USERS.id={user_id} and USERS.id=PLAYER_DATA.id"

def get_users_sql():
    return "SELECT * FROM USERSA"


def create_user_sql(user_id, username, email, is_admin):
    return f'INSERT INTO USERS VALUES ({user_id}, "{username}", "{email}", "", {is_admin})'


def update_user_sql(user_id, user: User):
    return f'UPDATE USERS SET username="{user.username}", email="{user.email}" WHERE id={user_id}'

def add_balance_sql(user_id, amount):
    return f"UPDATE PLAYER_DATA SET totalCurrency=totalCurrency+{amount} WHERE id={user_id};"

def deduct_balance_sql(user_id, amount):
    return f"UPDATE PLAYER_DATA SET totalCurrency=totalCurrency-{amount} WHERE id={user_id};"

def get_balance_sql(user_id):
    return f"SELECT totalCurrency from PLAYER_DATA WHERE id={user_id}"

def get_user_by_email_sql(email):
    return f"SELECT * FROM USERS WHERE email='{email}'"

def get_user_player_by_email_sql(email):
    return f"SELECT * FROM USERS, PLAYER_DATA WHERE USERS.email='{email}' and USERS.id=PLAYER_DATA.id"