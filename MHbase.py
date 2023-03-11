# miya.host base utilities.
import json
from datetime import datetime, timedelta, timezone
from utilities import MHdocker

from aiogram import types


def bignore(u: types.User):
    """
        Checks ignore list.
        :param u: User.
        :return: None.
    """
    database = json.load(open('haupt.json', 'r', encoding='utf-8'))
    langsam = json.load(open('verlangsamung.json', 'r', encoding='utf-8'))
    andere = json.load(open('anderequelle.json', 'r', encoding='utf-8'))
    user = u.id
    try:
        if database[str(user)]['banned']:
            return True
        if langsam[str(user)]['verlangsamt']:
            return True
        if andere['deadlock'] and u.id not in andere['admins']:
            return True
    except KeyError:
        return False
    return False


def expire(user: str) -> bool:
    """
        Checks if the user has expired.
        :param user: User.
        :return: If expired.
    """
    database = json.load(open('haupt.json', 'r', encoding='utf-8'))
    # Check if current time is greater than the expiration time and activated is True.
    if (
        database[user]['activated']
        and datetime.strptime(database[user]['datumbis'], '%H:%M:%S, %d.%m.%Y')
        < datetime.now()
    ):
        database[user]['activated'] = False
        database[user]['installed'] = False
        json.dump(database, open('haupt.json', 'w', encoding='utf-8'), indent=4)
        try:
            MHdocker.remove(user)
        except Exception:
            pass
        return True
    return False


def if_day_left(user: str) -> bool:
    """
        Checks if the user has a day left.
        :param user: User.
        :return: If a day left.
    """
    database = json.load(open('haupt.json', 'r', encoding='utf-8'))
    # Check if current time is greater than the expiration time and activated is True.
    if (
        database[user]['activated']
        and datetime.strptime(database[user]['datumbis'], '%H:%M:%S, %d.%m.%Y')
        < datetime.now() + timedelta(hours=21)
    ):
        try:
            if database[user]['endwarned']:
                return False
        except KeyError:
            pass
        database[user]['endwarned'] = True
        json.dump(database, open('haupt.json', 'w', encoding='utf-8'), indent=4)
        return True
    return False
