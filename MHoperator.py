# miya.host database operator.
import json


def get_user(user_id: int, key: str = ''):
    """
        Returns the value of the specified key for the specified user
        :param user_id: User ID.
        :param key: Key; may be not specified.
        :return: Value of the specified key for the specified user. If the key is not specified, returns the entire user's data. If the user is not found, returns None.
    """
    database = json.load(open('haupt.json', 'r', encoding='utf-8'))
    if not key:
        try:
            return database[str(user_id)]
        except KeyError:
            return None
    try:
        return database[str(user_id)][key]
    except KeyError:
        return None


def create_user(user_id: int, lang: str = 'en') -> bool:
    """
        Creates a new user in the database
        :param user_id: User ID
        :param lang: Language
        :return: True if the user was created successfully, False if the user already exists or failed doing I/O.
    """
    database = json.load(open('haupt.json', 'r', encoding='utf-8'))
    langsam = json.load(open('verlangsamung.json', 'r', encoding='utf-8'))
    if str(user_id) in database:
        return False
    database[str(user_id)] = {
        'lang': lang,
        'activated': False,
        'datumbis': '',
        "banned": False,
        'port': 0,
        'installed': False,
    }
    langsam[str(user_id)] = {
        "zahl": 0,
        "verlangsamt": False,
        "vzahl": 0,
        "vbis": "00:00:00, 01.01.2019"
    }
    try:
        json.dump(database, open('haupt.json', 'w', encoding='utf-8'), indent=4)
        json.dump(langsam, open('verlangsamung.json', 'w', encoding='utf-8'), indent=4)
        return True
    except Exception:
        return False


def edit_user(user_id: int, key: str, value) -> dict:
    """
        Edits the value of the specified key for the specified user.
        :param user_id: User ID.
        :param key: Key.
        :param value: Value.
        :return: The entire user's data. If the user is not found, returns empty dictionary.
    """
    database = json.load(open('haupt.json', 'r', encoding='utf-8'))
    database[str(user_id)][key] = value
    try:
        json.dump(database, open('haupt.json', 'w', encoding='utf-8'), indent=4)
        return database[str(user_id)]
    except Exception:
        return {}


def delete_user(user_id: int) -> bool:
    """
        Deletes the specified user from the database
        :param user_id: User ID.
        :return: True if the user was deleted successfully, False if the user does not exist or failed doing I/O.
    """
    database = json.load(open('haupt.json', 'r', encoding='utf-8'))
    langsam = json.load(open('verlangsamung.json', 'r', encoding='utf-8'))
    if str(user_id) not in database:
        return False
    del database[str(user_id)]
    del langsam[str(user_id)]
    try:
        json.dump(database, open('haupt.json', 'w', encoding='utf-8'), indent=4)
        json.dump(langsam, open('verlangsamung.json', 'w', encoding='utf-8'), indent=4)
        return True
    except Exception:
        return False


def vquelle(key: str, value) -> bool:
    """
        Edits the value of the specified key in side database.
        :param key: Key.
        :param value: Value.
        :return: The entire user's data. If the user is not found, returns empty dictionary.
    """
    andere = json.load(open('anderequelle.json', 'r', encoding='utf-8'))
    andere[key] = value
    try:
        json.dump(andere, open('anderequelle.json', 'w', encoding='utf-8'), indent=4)
        return True
    except Exception:
        return False


def equelle(key: str):
    """
        Returns the value of the specified key in side database.
        :param key: Key.
        :return: Value of the specified key in side database.If not found, returns None.
    """
    andere = json.load(open('anderequelle.json', 'r', encoding='utf-8'))
    try:
        return andere[key]
    except KeyError:
        return None
