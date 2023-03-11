# miya.host anti-flood protection system.
import json
from datetime import datetime, timedelta

from aiogram import types


async def do_routine(u: types.User) -> list:
    """
        Does routine operations.
        :param u: User.
        :return: List of suspended user's dictionary, integer, indicating warning level and suspencion time.
    """
    database = json.load(open('verlangsamung.json', 'r', encoding='utf-8'))
    database2 = json.load(open('haupt.json', 'r', encoding='utf-8'))
    database3 = json.load(open('anderequelle.json', 'r', encoding='utf-8'))
    if u.id in database3['admins']:
        return [{}, 0, '']

    database[str(u.id)]['zahl'] += 1
    if database[str(u.id)]['zahl'] >= 7:
        database[str(u.id)]['zahl'] = 0
        database[str(u.id)]['verlangsamt'] = True

        # First warning.
        if database[str(u.id)]['vzahl'] == 0:
            bzeit = (datetime.now() + timedelta(minutes=30)).strftime('%H:%M:%S, %d.%m.%Y')
            database[str(u.id)]['vbis'] = bzeit
            database[str(u.id)]['vzahl'] += 1
            json.dump(database, open('verlangsamung.json', 'w', encoding='utf-8'), indent=4)
            return [{str(u.id): database[str(u.id)]['vbis']}, 1, bzeit]
        # Second warning.
        elif database[str(u.id)]['vzahl'] == 1:
            bzeit = (datetime.now() + timedelta(hours=12)).strftime('%H:%M:%S, %d.%m.%Y')
            database[str(u.id)]['vbis'] = bzeit
            database[str(u.id)]['vzahl'] += 1
            json.dump(database, open('verlangsamung.json', 'w', encoding='utf-8'), indent=4)
            return [{str(u.id): database[str(u.id)]['vbis']}, 2, bzeit]

        # Third warning.
        elif database[str(u.id)]['vzahl'] == 2:
            bzeit = (datetime.now() + timedelta(days=7)).strftime('%H:%M:%S, %d.%m.%Y')
            database[str(u.id)]['vbis'] = bzeit
            database[str(u.id)]['vzahl'] += 1
            json.dump(database, open('verlangsamung.json', 'w', encoding='utf-8'), indent=4)
            return [{str(u.id): database[str(u.id)]['vbis']}, 3, bzeit]

        # Fourth warning.
        elif database[str(u.id)]['vzahl'] == 3:
            bzeit = (datetime.now() + timedelta(days=30)).strftime('%H:%M:%S, %d.%m.%Y')
            database[str(u.id)]['vbis'] = bzeit
            database[str(u.id)]['vzahl'] += 1
            json.dump(database, open('verlangsamung.json', 'w', encoding='utf-8'), indent=4)
            return [{str(u.id): database[str(u.id)]['vbis']}, 4, bzeit]

        # Suspension forever.
        elif database[str(u.id)]['vzahl'] == 4:
            bzeit = 'forever'
            database[str(u.id)]['vbis'] = bzeit
            database2[str(u.id)]['banned'] = True
            json.dump(database, open('verlangsamung.json', 'w', encoding='utf-8'), indent=4)
            json.dump(database2, open('haupt.json', 'w', encoding='utf-8'), indent=4)
            return [{str(u.id): database[str(u.id)]['vbis']}, 5, bzeit]

    else:
        json.dump(database, open('verlangsamung.json', 'w', encoding='utf-8'), indent=4)
        return [{}, 0, '']
    return [{}, 0, '']


# Must be called in a loop with a delay of 20 seconds.
async def clear_routine() -> None:
    """
        Clears routine operations.
        :return: None.
    """
    database = json.load(open('verlangsamung.json', 'r', encoding='utf-8'))
    for user in database:
        database[user]['zahl'] = 0
    json.dump(database, open('verlangsamung.json', 'w', encoding='utf-8'), indent=4)


async def blocktime_is_out() -> None:
    """
        Checks if the suspension time is over — if so, unblocks the user.
        :return: None.
    """
    database = json.load(open('verlangsamung.json', 'r', encoding='utf-8'))
    for user in database:
        if database[user]['verlangsamt']:
            if database[user]['vbis'] != 'forever':
                if datetime.now() > datetime.strptime(database[user]['vbis'], '%H:%M:%S, %d.%m.%Y'):
                    database[user]['verlangsamt'] = False
                    database[user]['vbis'] = ''
                    json.dump(database, open('verlangsamung.json', 'w', encoding='utf-8'), indent=4)
