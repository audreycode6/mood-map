from bcrypt import checkpw, gensalt, hashpw
from flask import g


def validate_registration(username, password):
    """
    check username and password is valid:
        - not empty
        - username is valid length
        - username doesnt exist in users table
    return list of errors (empty if valid input else list of error messages)
    """
    error_list = []
    user_exists = g.storage.user_exists(username)
    valid_user_length = len(username) <= 30

    if not valid_user_length:
        error_list.append(
            f"User '{username}' is too long. Please enter a username shorter than 30 characters."
        )

    if user_exists:
        error_list.append(f"User '{username}' already exists")

    if not username or not password:
        error_list.append("Missing input")

    return error_list


def get_hashed_pw_str(password):
    # Hash password
    hashed_pw = hashpw(password.encode("utf-8"), gensalt())
    # Convert to str before storing in db
    return hashed_pw.decode("utf-8")


def validate_login(username, password):
    """
    check input username and password is valid:
        - not empty
        - username exists in users table
        - input pw matches the hashed pw for associated username
    returns user_id if valid login, else False
    """
    if username and password:  # not missing input
        result = g.storage.user_exists(username)
        if result:  # valid user
            hashed_pw = result[2].encode("utf-8")
            b_pw = password.encode("utf-8")
            if checkpw(b_pw, hashed_pw):  # user input pw matches hashed pw
                return result[0]
    return False
