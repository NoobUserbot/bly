import asyncio
import contextlib
import json
import logging
import random
import re
from datetime import datetime, timedelta, timezone

import aioschedule as asch
from aiogram import Bot, Dispatcher, types, executor
from aiogram.utils.exceptions import MessageNotModified as MessageNotModifiedError

import MHoperator as op
import utilities.MHdocker as dckr
import utilities.MHbase as butils
import utilities.MHverlangsamer as lam
from utilities.MHuebersetz import TDS
import utilities.MHpayment as pymnt
import utilities.MHhiddenmethods as hmthds

PORTS_FORBIDDEN = [49002], [48666]
bot = Bot(token='6067131762:AAHO915Va8ahMjls3YNfsWarfuwXXEyOYCU', parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)
logging.getLogger('asch').setLevel(logging.CRITICAL)
logging.getLogger('schedule').setLevel(logging.CRITICAL)


@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    with contextlib.suppress(KeyError):
        if butils.bignore(m.from_user):
            return

        await suspend(m)
    
    keyb = types.InlineKeyboardMarkup()

    keyb.add(types.InlineKeyboardButton(text='EULA (RU)', url='https://telegra.ph/Usloviya-polzovaniya-servisom-miyahost-11-12'))
    keyb.insert(types.InlineKeyboardButton(text='EULA (EN)', url='https://telegra.ph/miyahost-EULA-EN-01-01'))

    if not op.get_user(m.from_user.id):
        ulang = m.from_user.language_code
        if ulang not in TDS().supported:
            ulang = 'en'
        op.create_user(m.from_user.id, ulang)
        await m.reply(TDS(m.from_user).get('defaultset_lang', ulang))
        return await m.reply(TDS(m.from_user).get('start') + f'\n{TDS(m.from_user).get("eula_autoaccept")}' , reply_markup=keyb)
    
    await m.reply(TDS(m.from_user).get('start'))


@dp.message_handler(commands=['help'])
async def help(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    tds = TDS(m.from_user)

    await m.answer(tds.get('help_message').format(op.equelle('version')), disable_web_page_preview=True)


@dp.message_handler(lambda m: m.text in ['/link', '/relogin', '🔗'])
async def link(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    if not op.get_user(m.from_user.id, 'installed'):
        return await m.reply(TDS(m.from_user).get('proc_err'))
    
    if not op.get_user(m.from_user.id, 'activated'):
        return await m.reply(TDS(m.from_user).get('no_subscription_e'))
    
    addr = dckr.cmodel['ip'] + op.get_user(str(m.from_user.id), 'port')
    if not op.get_user(m.from_user.id, 'installed') or not op.get_user(m.from_user.id, 'activated'):
        return await m.reply(TDS(m.from_user).get('proc_err'))
    await m.reply(TDS(m.from_user).get('login_message').format(addr, TDS(m.from_user).get('privacy_alert')))


@dp.message_handler(commands=['setlang'])
async def setlang(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    if m.get_args():
        if m.get_args() in TDS().supported:
            op.edit_user(m.from_user.id, 'lang', m.get_args())
            await m.reply(TDS(m.from_user).get('langset', m.get_args()))  # type: ignore
        else:
            await m.reply(TDS(m.from_user).get('language?!'))

    else:
        keyb = types.InlineKeyboardMarkup(
            2,
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(text='🇷🇺 Русский', callback_data='lang:ru'),
                    types.InlineKeyboardButton(text='🇬🇧 English', callback_data='lang:en'),
                ],
                [
                    types.InlineKeyboardButton(text='🇩🇪 Deutsch', callback_data='lang:de'),
                    types.InlineKeyboardButton(text='🇳🇱 Nederlands', callback_data='lang:nl'),
                ],
                [
                    types.InlineKeyboardButton(text='🇺🇦 Українська', callback_data='lang:uk'),
                    types.InlineKeyboardButton(text='🇪🇸 Español', callback_data='lang:es'),
                ],
                [
                    types.InlineKeyboardButton(text='🇫🇷 Français', callback_data='lang:fr'),
                    types.InlineKeyboardButton(text='🇮🇹 Italiano', callback_data='lang:it'),
                ],
                [
                    types.InlineKeyboardButton(text='🇺🇿 O‘zbek', callback_data='lang:uz'),
                    types.InlineKeyboardButton(text='(TT) Татар', callback_data='lang:tt'),
                ],
            ]
        )
        await m.reply(TDS(m.from_user).get('language?'), reply_markup=keyb)


@dp.callback_query_handler(lambda c: c.data.startswith('lang:'))
async def setlang_callback(c: types.CallbackQuery):
    if butils.bignore(c.from_user):
        return

    await suspend(c.message.reply_to_message)

    lang = c.data.split(':')[1]
    if lang in TDS().supported:
        keyb = types.InlineKeyboardMarkup(
            2,
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(text='🇷🇺 Русский', callback_data='lang:ru'),
                    types.InlineKeyboardButton(text='🇬🇧 English', callback_data='lang:en'),
                ],
                [
                    types.InlineKeyboardButton(text='🇩🇪 Deutsch', callback_data='lang:de'),
                    types.InlineKeyboardButton(text='🇳🇱 Nederlands', callback_data='lang:nl'),
                ],
                [
                    types.InlineKeyboardButton(text='🇺🇦 Українська', callback_data='lang:uk'),
                    types.InlineKeyboardButton(text='🇪🇸 Español', callback_data='lang:es'),
                ],
                [
                    types.InlineKeyboardButton(text='🇫🇷 Français', callback_data='lang:fr'),
                    types.InlineKeyboardButton(text='🇮🇹 Italiano', callback_data='lang:it'),
                ],
                [
                    types.InlineKeyboardButton(text='🇺🇿 O‘zbek', callback_data='lang:uz'),
                    types.InlineKeyboardButton(text='(TT) Татар', callback_data='lang:tt'),
                ],
            ]
        )
        cur_lang = op.get_user(c.from_user.id, 'lang')
        if cur_lang == lang:
            return
        op.edit_user(c.from_user.id, 'lang', lang)
        try:
            await c.message.edit_text(TDS().get('language?', lang=lang), reply_markup=keyb)
            await c.answer(re.sub(r'<.{1,4}>', '', TDS().get('proc_done', lang=lang)), True)
        except:
            return


@dp.message_handler(commands=['deadlock'])
async def deadlock(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    if m.from_user.id not in op.equelle('admins'):  # type: ignore
        return await m.reply(TDS(m.from_user).get('no_rights'))

    if op.equelle('deadlock'):
        await m.reply(TDS(m.from_user).get('deadlock').format('🔒', 'on'))
    else:
        await m.reply(TDS(m.from_user).get('deadlock').format('🔓', 'off'))


@dp.message_handler(commands=['cdeadlock'])
async def cdeadlock(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    if m.from_user.id not in op.equelle('admins'):  # type: ignore
        return await m.reply(TDS(m.from_user).get('no_rights'))

    if op.equelle('deadlock'):
        await m.reply(TDS(m.from_user).get('deadlock_switch').format('🔓', 'off'))
        op.vquelle('deadlock', False)
    else:
        await m.reply(TDS(m.from_user).get('deadlock_switch').format('🔒', 'on'))
        op.vquelle('deadlock', True)


@dp.message_handler(commands=['madd'])
async def madd(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    if m.from_user.id not in op.equelle('admins'):  # type: ignore
        return await m.reply(TDS(m.from_user).get('no_rights'))

    if not m.get_args():
        return await m.reply(TDS(m.from_user).get('args?'))

    if not m.get_args().isnumeric():
        return await m.reply(TDS(m.from_user).get('args?!'))

    if op.get_user(m.get_args()):  # type: ignore
        return await m.reply(TDS(m.from_user).get('args?!'))

    op.create_user(int(m.get_args()), 'en')  # type: ignore
    await m.reply(TDS(m.from_user).get('added_user'))


@dp.message_handler(commands=['mdel'])
async def mdel(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    if m.from_user.id not in op.equelle('admins'):  # type: ignore
        return await m.reply(TDS(m.from_user).get('no_rights'))

    if not m.get_args():
        return await m.reply(TDS(m.from_user).get('args?'))

    if not m.get_args().isnumeric():
        return await m.reply(TDS(m.from_user).get('args?!'))

    if op.get_user(int(m.get_args())):  # type: ignore
        deleted = op.delete_user(int(m.get_args()))  # type: ignore
        try:
            dckr.remove((m.get_args()))
        except:
            pass
    else:
        deleted = False

    if deleted:
        await m.reply(TDS(m.from_user).get('removed_user'))
    else:
        await m.reply(TDS(m.from_user).get('user_not_found'))


@dp.message_handler(commands=['mban'])
async def mban(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    if m.from_user.id not in op.equelle('admins'):  # type: ignore
        return await m.reply(TDS(m.from_user).get('no_rights'))

    if not m.get_args():
        return await m.reply(TDS(m.from_user).get('args?'))

    if '\n' in m.get_args():  # type: ignore
        user, reason = m.get_args().split('\n', 1)
    else:
        user, reason = m.get_args(), 'no reason'

    if not user.isnumeric():
        return await m.reply(TDS(m.from_user).get('args?!'))

    if not op.get_user(int(user)):  # type: ignore
        return await m.reply(TDS(m.from_user).get('user_not_found'))

    keyb = types.InlineKeyboardMarkup()
    keyb.add(types.InlineKeyboardButton(text=TDS(m.from_user).get('yes'), callback_data='ban'))
    keyb.add(types.InlineKeyboardButton(text=TDS(m.from_user).get('no'), callback_data='cancel'))

    await m.reply(TDS(m.from_user).get('confirm_ban').format(user, reason), reply_markup=keyb)


@dp.message_handler(commands=['mern'])
async def mern(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    if m.from_user.id not in op.equelle('admins'):  # type: ignore
        return await m.reply(TDS(m.from_user).get('no_rights'))

    if not m.get_args():
        return await m.reply(TDS(m.from_user).get('args?'))

    if '\n' in m.get_args():  # type: ignore
        user, length = m.get_args().split('\n', 1)
    else:
        user, length = m.get_args(), '1'

    if not user.isnumeric():
        return await m.reply(TDS(m.from_user).get('args?!'))

    if not length.isnumeric():
        return await m.reply(TDS(m.from_user).get('args?!'))

    if not op.get_user(int(user)):  # type: ignore
        op.create_user(int(user), 'en')  # type: ignore
        op.edit_user(int(user), 'datumbis',
                     (datetime.now() + timedelta(days=int(length))).strftime('%H:%M:%S, %d.%m.%Y'))  # type: ignore
        return await m.reply(TDS(m.from_user).get('proc_done'))

    if op.get_user(int(user))['datumbis'] == '':
        op.edit_user(int(user), 'datumbis',
                        (datetime.now() + timedelta(days=int(length))).strftime('%H:%M:%S, %d.%m.%Y'))  # type: ignore
        op.edit_user(int(user), 'activated', True)  # type: ignore
        return await m.reply(TDS(m.from_user).get('proc_done'))

    elif datetime.strptime(op.get_user(int(user))['datumbis'], '%H:%M:%S, %d.%m.%Y') < datetime.now():  # type: ignore
        op.edit_user(int(user), 'datumbis',
                     (datetime.now() + timedelta(days=int(length))).strftime('%H:%M:%S, %d.%m.%Y'))  # type: ignore
        op.edit_user(int(user), 'activated', True)  # type: ignore
        return await m.reply(TDS(m.from_user).get('proc_done'))

    op.edit_user(int(user), 'datumbis', (datetime.strptime(op.get_user(int(user))['datumbis'], '%H:%M:%S, %d.%m.%Y') + timedelta(
        days=int(length))).strftime('%H:%M:%S, %d.%m.%Y'))  # type: ignore
    await m.reply(TDS(m.from_user).get('proc_done'))


@dp.message_handler(commands=['gsend'])
async def gsend(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    if m.from_user.id not in op.equelle('admins'):  # type: ignore
        return await m.reply(TDS(m.from_user).get('no_rights'))

    if not m.get_args():
        return await m.reply(TDS(m.from_user).get('args?'))

    database = json.load(open('haupt.json', 'r', encoding='utf-8'))
    andere = json.load(open('anderequelle.json', 'r'))

    for user in database.keys():
        try:
            if not database[user]['banned'] and int(user) not in andere['admins']:
                await bot.send_message(user, m.get_args(), parse_mode='Markdown')
        except:
            pass

    await m.reply(TDS(m.from_user).get('proc_done'))


@dp.message_handler(commands=['muban'])
async def muban(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    if m.from_user.id not in op.equelle('admins'):  # type: ignore
        return await m.reply(TDS(m.from_user).get('no_rights'))

    if not m.get_args():
        return await m.reply(TDS(m.from_user).get('args?'))

    if not m.get_args().isnumeric():
        return await m.reply(TDS(m.from_user).get('args?!'))

    if not op.get_user(int(m.get_args())):  # type: ignore
        return await m.reply(TDS(m.from_user).get('user_not_found'))

    if not op.get_user(int(m.get_args()))['banned']:  # type: ignore
        return await m.reply(TDS(m.from_user).get('args?!'))

    keyb = types.InlineKeyboardMarkup()
    keyb.add(types.InlineKeyboardButton(text=TDS(m.from_user).get('yes'), callback_data='unban'))
    keyb.add(types.InlineKeyboardButton(text=TDS(m.from_user).get('no'), callback_data='cancel'))

    await m.reply(TDS(m.from_user).get('confirm_unban').format(m.get_args()), reply_markup=keyb)


@dp.message_handler(lambda m: m.text[:2] == '/h' and not m.text.startswith('/help'))
async def hidden(m: types.Message):
    if butils.bignore(m.from_user):
        return

    tds = TDS(m.from_user)

    await suspend(m)

    method = m.text.split(' ')[0][2:]
    user = m.from_user.id
    mentions = [' there', ', mate', ', bro', ', dude', ', pal', ', friend', ', buddy']
    accept = ['Yep, I am!', 'I\'m sure!', 'I\'m in!', 'Just do it!', 'Yeah, why not?']
    reject = ['Nope, I\'m not!', 'I\'m not sure!', 'I\'m out!', 'No, thanks!', 'Get out of me!']
    base = f'<b>Hello{random.choice(mentions)}!</b>\nThat\'s me, usual reminder about hidden methods.\n\nPlease, remember that hidden methods not supposed to be frequent used and extremly dangerous for user, who doesn\'t know, what he\'s doing. If you\'re really wanna execute it, let me remind you, what <code>{method}</> method does.\n'+ '<code>{}</>'

    if method == 'rollback':
        keyb = types.InlineKeyboardMarkup()
        keyb.add(types.InlineKeyboardButton(text=tds.get('yes'), callback_data='rollback'))
        keyb.add(types.InlineKeyboardButton(text=tds.get('no'), callback_data='cancel'))
        return await m.reply(tds.get('hm.rollback', '', 'a'), reply_markup=keyb)
    
    if method == 'ckblang':
        keyb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyb.add(types.KeyboardButton(text=TDS(m.from_user).get('start_button')), types.KeyboardButton(text=TDS(m.from_user).get('stop_button')))
        keyb.add(types.KeyboardButton(text=TDS(m.from_user).get('restart_button')))
        return await m.reply(f'🫥{TDS(m.from_user).get("proc_done")[1:]}', reply_markup=keyb)
    
    if method == 'ccommands':
        if m.from_user.id not in op.equelle('admins'):
            return await m.reply(tds.get('exposed_easteregg', '', 'a'))
        commands = json.load(open('utilities/ctds.json', 'r', encoding='utf-8'))
        for lang in commands.keys():
            if lang == 'en':
                await bot.set_my_commands(form_commands_array(commands[lang]), types.BotCommandScopeDefault())
            else:
                await bot.set_my_commands(form_commands_array(commands[lang]), types.BotCommandScopeDefault(), language_code=lang)
        return await m.reply(f'🫥{TDS(m.from_user).get("proc_done")[1:]}')
    
    if method == 'httpauth':
        api_keys = json.load(open('auth.json', 'r', encoding='utf-8'))
        if m.from_user.id != m.chat.id:
            return await m.reply(tds.get('PrivacyThreat', '', 'e'))

        if str(m.from_user.id) not in api_keys.keys():
            import string
            basic_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            api_keys[str(m.from_user.id)] = {'basic': basic_key}
            json.dump(api_keys, open('auth.json', 'w', encoding='utf-8'), indent=4)
            return await m.reply(tds.get('api_auth', '', 'a').format(basic_key))
        else:
            return await m.reply(tds.get('api_auth', '', 'a').format(api_keys[str(m.from_user.id)]["basic"]))
    
    if method == 'revokehttpauth':
        api_keys = json.load(open('auth.json', 'r', encoding='utf-8'))

        if str(m.from_user.id) not in api_keys.keys():
            return await m.reply(tds.get('no_api_keys', '', 'a'))
        
        del api_keys[str(m.from_user.id)]
        json.dump(api_keys, open('auth.json', 'w', encoding='utf-8'), indent=4)
        return await m.reply(tds.get('api_revoked', '', 'a'))
    
    if method == 'mockcreds':
        args = m.text.split(' ')
        if len(args) != 3:
            return await m.reply(tds.get('error_easteregg', '', 'a'))
        _, end_id, end_key = args
        if not end_id.isdigit():
            return await m.reply(tds.get('error_easteregg', '', 'a'))
        if len(end_key) != 16:
            return await m.reply(tds.get('error_easteregg', '', 'a'))
        api_keys = json.load(open('auth.json', 'r', encoding='utf-8'))
        data = json.load(open('haupt.json', 'r', encoding='utf-8'))
        if end_id not in data.keys():
            return await m.reply(tds.get('error_easteregg', '', 'a'))
        if end_id not in api_keys.keys():
            return await m.reply(tds.get('error_easteregg', '', 'a'))
        if end_key != api_keys[end_id]['basic']:
            return await m.reply(tds.get('error_easteregg', '', 'a'))
        
        data[str(m.from_user.id)]['mocking_auth'] = {'id': end_id, 'basic_key': end_key}
        json.dump(data, open('haupt.json', 'w', encoding='utf-8'), indent=4)
        return await m.reply(tds.get('mocking_setup', '', 'a'))
    
    if method == 'dmockcreds':
        data = json.load(open('haupt.json', 'r', encoding='utf-8'))
        if 'mocking_auth' not in data[str(m.from_user.id)].keys():
            return await m.reply(tds.get('error_easteregg', '', 'a'))
        del data[str(m.from_user.id)]['mocking_auth']
        json.dump(data, open('haupt.json', 'w', encoding='utf-8'), indent=4)
        return await m.reply(tds.get('mocking_reset', '', 'a'))


    else:
        await m.reply(tds.get('error_easteregg', '', 'a'))


@dp.callback_query_handler(lambda c: c.data == 'rollback')
async def rollback(c: types.CallbackQuery):
    if butils.bignore(c.from_user):
        return

    await suspend(c.message.reply_to_message)

    await c.message.edit_text(TDS(c.from_user).get('await_0'))
    result = await hmthds.rollback(c.from_user.id)
    if result is True:
        await c.message.edit_text(TDS(c.from_user).get('proc_done'))
    else:
        await c.message.edit_text(TDS(c.from_user).get('proc_err') + '\n' + result)


@dp.message_handler(lambda m: m.text[:2] == '🔄 ' or m.text == '/restart')
async def refresh(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    tds = TDS(m.from_user)

    nm = await m.answer(tds.get('restarting'))
    try:
        await dckr.restart(str(m.from_user.id))
        await nm.edit_text(tds.get('proc_done'))
    except dckr.docker.errors.NotFound as e:
        error_description = f'{tds.get("possible_cause", additional_file="e").format(tds.get("DockerNotFound", additional_file="e"))}'
        await nm.edit_text(f"{tds.get('proc_err')}\n{error_description}")
        logging.error(e)
    except dckr.docker.errors.APIError as e:
        error_description = f'{tds.get("possible_cause", additional_file="e").format(tds.get("DockerAlreadyExists", additional_file="e"))}'
        await nm.edit_text(f"{tds.get('proc_err')}\n{error_description}")
        logging.error(e)
    except Exception as e:
        await nm.edit_text(f"{tds.get('proc_err')}\n{e}")
        logging.error(e)


@dp.message_handler(lambda m: m.text[:2] == '⏸ ' or m.text == '/pause')
async def pause(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    tds = TDS(m.from_user)

    nm = await m.answer(tds.get('stopping'))
    try:
        dckr.stop(str(m.from_user.id))
        await nm.edit_text(tds.get('proc_done'))
    except dckr.docker.errors.NotFound as e:
        error_description = f'{tds.get("possible_cause", additional_file="e").format(tds.get("DockerNotFound", additional_file="e"))}'
        await nm.edit_text(f"{tds.get('proc_err')}\n{error_description}")
        logging.error(e)
    except dckr.docker.errors.APIError as e:
        error_description = f'{tds.get("possible_cause", additional_file="e").format(tds.get("DockerAlreadyExists", additional_file="e"))}'
        await nm.edit_text(f"{tds.get('proc_err')}\n{error_description}")
        logging.error(e)
    except Exception as e:
        await nm.edit_text(tds.get('proc_err') + f'\n<code>{e}</>')
        logging.error(e)


@dp.message_handler(lambda m: m.text[:2] == '▶ ' or m.text == '/strt')
async def start(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    tds = TDS(m.from_user)

    nm = await m.answer(tds.get('starting'))
    try:
        dckr.start(str(m.from_user.id))
        await nm.edit_text(tds.get('proc_done'))
    except dckr.docker.errors.NotFound as e:
        error_description = f'{tds.get("possible_cause", additional_file="e").format(tds.get("DockerNotFound", additional_file="e"))}'
        await nm.edit_text(f"{tds.get('proc_err')}\n{error_description}")
        logging.error(e)
    except dckr.docker.errors.APIError as e:
        error_description = f'{tds.get("possible_cause", additional_file="e").format(tds.get("DockerAlreadyExists", additional_file="e"))}'
        await nm.edit_text(f"{tds.get('proc_err')}\n{error_description}")
        logging.error(e)
    except Exception as e:
        await nm.edit_text(tds.get('proc_err') + f'\n<code>{e}</>')
        logging.error(e)


@dp.message_handler(commands=['delete'])
async def delete(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    tds = TDS(m.from_user)
    from aiogram.types import ReplyKeyboardRemove

    nm = await m.reply(tds.get('await_0'))
    try:
        dckr.remove(str(m.from_user.id))
        await nm.edit_text(tds.get('proc_done'))
        op.edit_user(m.from_user.id, 'installed', False)
    except dckr.docker.errors.NotFound as e:
        error_description = f'{tds.get("possible_cause", additional_file="e").format(tds.get("DockerNotFound", additional_file="e"))}'
        await nm.edit_text(f"{tds.get('proc_err')}\n{error_description}")
        logging.error(e)
    except Exception as e:
        await nm.edit_text(tds.get('proc_err') + f'\n<code>{e}</>')


@dp.message_handler(commands=['install'])
async def install(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    tds = TDS(m.from_user)

    if not op.get_user(str(m.from_user.id), 'activated'):
        return await m.answer(tds.get('no_subscription_e'))

    nm = await m.answer(tds.get('await_0'))
    try:
        datab = json.load(open('haupt.json', 'r', encoding='utf-8'))
        ports: tuple = tuple(datab[user]['port'] for user in datab.keys())
        port = random.randint(48001, 49200)
        while port in ports or port in PORTS_FORBIDDEN:
                port = random.randint(48003, 49200)
        op.edit_user(str(m.from_user.id), 'port', str(port))

        while True:
            try:
                dckr.create(port, str(m.from_user.id))
                break
            except dckr.docker.errors.APIError as e:
                text = str(e)
                if 'port is already allocated' in text:
                    port = random.randint(48001, 49200)
                    while port in ports or port in PORTS_FORBIDDEN:
                        port = random.randint(48001, 49200)
                    op.edit_user(str(m.from_user.id), 'port', str(port))
                else:
                    raise e
        
        addr = dckr.cmodel['ip'] + op.get_user(str(m.from_user.id), 'port')
        await nm.delete()
        keyb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyb.add(types.KeyboardButton(text=tds.get('start_button')), types.KeyboardButton(text=tds.get('stop_button')))
        keyb.add(types.KeyboardButton(text=tds.get('restart_button')))
        await m.reply(tds.get('login_message').format(addr, tds.get('privacy_alert')), reply_markup=keyb)
        op.edit_user(str(m.from_user.id), 'installed', True)
    except dckr.docker.errors.APIError as e:
        error_description = f'{tds.get("possible_cause", additional_file="e").format(tds.get("DockerAlreadyExists", additional_file="e"))}'
        await nm.edit_text(f"{tds.get('proc_err')}\n{error_description}")
        logging.error(e)
    except Exception as e:
        await nm.edit_text(tds.get('proc_err') + f'\n<code>{e}</>')


@dp.message_handler(commands=['pay'])
async def pay(m: types.Message):
    if butils.bignore(m.from_user):
        return

    await suspend(m)

    if m.from_user.id != m.chat.id:
        return await m.reply(TDS(m.from_user).get('PrivacyThreat', '', 'e'))

    keyb = types.InlineKeyboardMarkup(
        1,
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text='🟠 QIWI',
                    callback_data='qiwi_select'
                ),

                types.InlineKeyboardButton(
                    text='🟣 YooMoney',
                    callback_data='yoo_select'
                )
            ],
            [
                types.InlineKeyboardButton(
                    text='💎 CryptoBot',
                    callback_data='crypto_select'
                )
            ]
        ]
    )

    await m.reply(TDS(m.from_user).get('platform_choice'), reply_markup=keyb)


@dp.callback_query_handler(lambda c: c.data == 'qiwi_select')
async def qiwi_select(c: types.CallbackQuery):
    if butils.bignore(c.from_user):
        return

    await suspend(c.message.reply_to_message)

    #return await c.answer(TDS(c.from_user).get('disabled', '', 'e'))

    keyb = types.InlineKeyboardMarkup(
        1,
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=TDS(c.from_user).get('payment_button'),
                    url=pymnt.create_invoice(recipient=c.from_user.id)
                ),

                types.InlineKeyboardButton(
                    text=TDS(c.from_user).get('pcheck_button'),
                    callback_data=f'check_payment:q:{c.from_user.id}'
                ),
            ]
        ]
    )

    await c.message.edit_text(TDS(c.from_user).get('payment_template').format(f'{op.equelle("price")} RUB', 'QIWI'), reply_markup=keyb)


@dp.callback_query_handler(lambda c: c.data == 'yoo_select')
async def yoo_select(c: types.CallbackQuery):
    if butils.bignore(c.from_user):
        return

    await suspend(c.message.reply_to_message)

    keyb = types.InlineKeyboardMarkup(
        1,
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=TDS(c.from_user).get('payment_button'),
                    url=pymnt.create_invoice('y', c.from_user.id)
                ),

                types.InlineKeyboardButton(
                    text=TDS(c.from_user).get('pcheck_button'),
                    callback_data=f'check_payment:y:{c.from_user.id}'
                ),
            ]
        ]
    )

    await c.message.edit_text(TDS(c.from_user).get('payment_template').format(f'{op.equelle("price")} RUB', 'YooMoney'), reply_markup=keyb)


@dp.callback_query_handler(lambda c: c.data == 'crypto_select')
async def crypto_select(c: types.CallbackQuery):
    if butils.bignore(c.from_user):
        return

    await suspend(c.message.reply_to_message)

    keyb = types.InlineKeyboardMarkup(
        3,
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text='🟡 BTC',
                    callback_data='crypto_select:btc'
                ),

                types.InlineKeyboardButton(
                    text='🔵 TON',
                    callback_data=f'crypto_select:ton'
                ),
                types.InlineKeyboardButton(
                    text='🟢 USDT',
                    callback_data='crypto_select:usdt'
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text='🟨 BUSD',
                    callback_data='crypto_select:busd'
                ),
                types.InlineKeyboardButton(
                    text='⬛ ETH',
                    callback_data='crypto_select:eth'
                ),
                types.InlineKeyboardButton(
                    text='🟦 USDC',
                    callback_data='crypto_select:usdc'
                )
            ]
        ]
    )

    await c.message.edit_text(TDS(c.from_user).get('payment_template').format(f'{op.equelle("price")} RUB', 'CryptoBot'), reply_markup=keyb)


@dp.callback_query_handler(lambda c: c.data.split(':')[0] == 'crypto_select')
async def crypto_select_2(c: types.CallbackQuery):
    crypto = c.data.split(':')[1].upper()

    req = pymnt.create_invoice('c', c.from_user.id, pymnt._get_crypto_exr(crypto), cc=crypto)
    keyb = types.InlineKeyboardMarkup(
        1,
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=TDS(c.from_user).get('payment_button'),
                    url=req
                ),

                types.InlineKeyboardButton(
                    text=TDS(c.from_user).get('pcheck_button'),
                    callback_data=f'check_payment:c:{c.from_user.id}'
                ),
            ]
        ]
    )
    await c.message.edit_text(TDS(c.from_user).get('payment_template').format(f'{pymnt._get_crypto_exr(crypto)} {crypto}', 'CryptoBot'), reply_markup=keyb)


@dp.callback_query_handler(lambda c: c.data.split(':')[0] == 'check_payment')
async def check_payment(c: types.CallbackQuery):
    if butils.bignore(c.from_user):
        return

    await suspend(c.message.reply_to_message)

    _, platform, user_id = c.data.split(':')
    user_id = int(user_id)

    tds = TDS(c.from_user)

    if not pymnt.check_payment(user_id, platform):
        try:
            return await c.answer(
                re.sub(r'<.{1,4}>', '', tds.get('proc_err'))
            )
        except:
            return

    await c.message.edit_text(tds.get('pay_done'))

    if not op.get_user(user_id, 'activated') or not op.get_user(user_id, 'installed'):
        with open('haupt.json', 'r', encoding='utf-8') as f:
            datab = json.load(f)
        ports: tuple = tuple(datab[user]['port'] for user in datab.keys())
        port = random.randint(48001, 49200)
        while port in ports or port in PORTS_FORBIDDEN:
            port = random.randint(48001, 49200)

        while True:
            try:
                dckr.create(port, user_id)
                break
            except dckr.docker.errors.APIError as e:
                text = str(e)
                if 'port is already allocated' in text:
                    port = random.randint(48001, 49200)
                    while port in ports or port in PORTS_FORBIDDEN:
                        port = random.randint(48001, 49200)
                else:
                    raise e

        op.edit_user(user_id, 'activated', True)
        op.edit_user(user_id, 'port', str(port))
        abgelauft = (datetime.now(tz=timezone(timedelta(hours=3))) + timedelta(days=30)).strftime('%H:%M:%S, %d.%m.%Y')

    else:
        abgelauft = (
                datetime.strptime(op.get_user(user_id, 'datumbis'),
                                  '%H:%M:%S, %d.%m.%Y') + timedelta(days=30)).strftime('%H:%M:%S, %d.%m.%Y')

    op.edit_user(user_id, 'datumbis', abgelauft)

    addr = dckr.cmodel['ip'] + op.get_user(user_id, 'port')
    nm = await c.message.reply_to_message.reply(tds.get('await_nf'))
    await asyncio.sleep(15)
    await nm.delete()
    keyb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyb.add(types.KeyboardButton(text=tds.get('start_button')), types.KeyboardButton(text=tds.get('stop_button')))
    keyb.add(types.KeyboardButton(text=tds.get('restart_button')))
    await c.message.reply_to_message.reply(tds.get('login_message').format(addr, tds.get('privacy_alert')))
    op.edit_user(user_id, 'installed', True)


@dp.callback_query_handler(lambda c: c.data == 'ban')
async def ban(c: types.CallbackQuery):
    if butils.bignore(c.from_user):
        return

    await suspend(c.message.reply_to_message)

    if c.from_user.id not in op.equelle('admins'):  # type: ignore
        try:
            return await c.answer(TDS(c.from_user).get(f'notyourthing{random.randint(1, 4)}'))
        except:
            return

    ouser = c.message.reply_to_message.from_user.id
    buser = re.sub(r'[^0-9]', '', c.message.text.splitlines()[2])

    if c.from_user.id != ouser:
        try:
            return await c.answer(TDS(c.from_user).get(f'notyourthing{random.randint(1, 4)}'))
        except:
            return

    op.edit_user(buser, 'banned', True)  # type: ignore
    try:
        dckr.remove(buser)
    except:
        pass
    await c.message.edit_text(TDS(c.from_user).get('done_ban').format(buser))


@dp.callback_query_handler(lambda c: c.data == 'unban')
async def unban(c: types.CallbackQuery):
    if butils.bignore(c.from_user):
        return

    await suspend(c.message.reply_to_message)

    if c.from_user.id not in op.equelle('admins'):  # type: ignore
        try:
            return await c.answer(TDS(c.from_user).get(f'notyourthing{random.randint(1, 4)}'))
        except:
            return

    ouser = c.message.reply_to_message.from_user.id
    buser = re.sub(r'[^0-9]', '', c.message.text)

    if c.from_user.id != ouser:
        try:
            return await c.answer(TDS(c.from_user).get(f'notyourthing{random.randint(1, 4)}'))
        except:
            return

    op.edit_user(buser, 'banned', False)  # type: ignore
    await c.message.edit_text(TDS(c.from_user).get('done_unban').format(buser))


@dp.callback_query_handler(lambda c: c.data == 'cancel')
async def cancel(c: types.CallbackQuery):
    if butils.bignore(c.from_user):
        return

    await suspend(c.message.reply_to_message)

    await c.message.edit_text(TDS(c.from_user).get('cancelled'))


def get_running_menu(tds: TDS, user_id: int):
    reply_markup: types.InlineKeyboardMarkup = types.InlineKeyboardMarkup()

    for label, callback_data in (
            ('restart_button', f'restart_container:{user_id}'),
            ('stop_button', f'stop_container:{user_id}')
    ):
        reply_markup.insert(
            types.InlineKeyboardButton(
                tds.get(label),
                callback_data=callback_data
            )
        )

    return reply_markup


def get_mock_running_menu(tds: TDS, user_id: int):
    reply_markup: types.InlineKeyboardMarkup = types.InlineKeyboardMarkup()

    for label, callback_data in (
            ('restart_button', f'mock_restart_container:{user_id}'),
            ('stop_button', f'mock_stop_container:{user_id}')
    ):
        reply_markup.insert(
            types.InlineKeyboardButton(
                f'(⚫) {tds.get(label)}',
                callback_data=callback_data
            )
        )

    return reply_markup


def get_inactive_menu(tds: TDS, user_id: int):
    reply_markup: types.InlineKeyboardMarkup = types.InlineKeyboardMarkup()

    reply_markup.insert(
        types.InlineKeyboardButton(
            tds.get("start_button"),
            callback_data=f'start_container:{user_id}'
        )
    )

    return reply_markup


def get_mock_inactive_menu(tds: TDS, user_id: int):
    reply_markup: types.InlineKeyboardMarkup = types.InlineKeyboardMarkup()

    reply_markup.insert(
        types.InlineKeyboardButton(
            f'(⚫) {tds.get("start_button")}',
            callback_data=f'mock_start_container:{user_id}'
        )
    )

    return reply_markup


@dp.inline_handler()
async def get_menu(q: types.InlineQuery):
    if butils.bignore(q.from_user):
        return

    user_id: str = str(q.from_user.id)
    mock = False
    tds: TDS = TDS(q.from_user)

    with open('haupt.json') as file:
        try:
            data: dict = json.load(file)
        except json.JSONDecodeError:
            print('Duck you')
    
    if user_id in data.keys() and 'mocking_auth' in data[user_id].keys():
        user_id = data[user_id]['mocking_auth']['id']
        mock = True
    
    if user_id not in data.keys() or not data[user_id]["activated"]:
        return await q.answer(
            [
                types.InlineQueryResultArticle(
                    id='1',
                    title=tds.get('no_subscription'),
                    input_message_content=types.InputTextMessageContent(
                        tds.get('no_subscription_e')
                    )
                )
            ],
            cache_time=0,
            is_personal=True
        )
    

    
    elif user_id in data.keys() and not data[user_id]["installed"]:
        return await q.answer(
            [
                types.InlineQueryResultArticle(
                    id='1',
                    title=re.sub(r'<.{1,4}>', '', tds.get('proc_err')),
                    description=re.sub(r'<.{1,4}>', '', tds.get("possible_cause", additional_file="e").format(tds.get("DockerNotFound", additional_file="e"))),
                    input_message_content=types.InputTextMessageContent(
                        tds.get('proc_err') + '\n' + tds.get("possible_cause", additional_file="e").format(tds.get("DockerNotFound", additional_file="e"))
                    )
                )
            ],
            cache_time=0,
            is_personal=True
        )

    reply_markup: types.InlineKeyboardMarkup
    container = dckr.get(user_id)
    match container.status:
        case 'running' | 'restarting':
            reply_markup = get_running_menu(tds, int(user_id)) if not mock else get_mock_running_menu(tds, int(user_id))
            cased_body = tds.get('menu_body').format(tds.get('state_on'), op.get_user(user_id, 'datumbis')) + f'\nID: {user_id}' if not mock else f"⚫{tds.get('menu_body')[1:]}".format(tds.get('state_on'), op.get_user(user_id, 'datumbis')) + f'\nID: {user_id}'
        case _:
            reply_markup = get_inactive_menu(tds, int(user_id)) if not mock else get_mock_inactive_menu(tds, int(user_id))
            cased_body = tds.get('menu_body').format(tds.get('state_off'), op.get_user(user_id, 'datumbis')) + f'\nID: {user_id}' if not mock else f"⚫{tds.get('menu_body')[1:]}".format(tds.get('state_off'), op.get_user(user_id, 'datumbis')) + f'\nID: {user_id}'
    await q.answer(
        [
            types.InlineQueryResultArticle(
                id='0',
                title=tds.get('menu_title'),
                input_message_content=types.InputTextMessageContent(
                    cased_body
                ),
                reply_markup=reply_markup,
                description=f'⚫ {user_id}' if mock else None
            )
        ],
        cache_time=0,
        is_personal=True
    )


@dp.callback_query_handler(
    lambda c: c.data.split(':')[0] in (
            'start_container',
            'stop_container',
            'restart_container'
    )
)
async def container_callback_handler(c: types.CallbackQuery):
    if butils.bignore(c.from_user):
        return

    tds: TDS = TDS(c.from_user)
    target = str(c.from_user.id)

    try:
        if target != c.data.split(':')[1]:
            try:
                return await c.answer(tds.get(f'notyourthing{random.randint(1, 4)}'))
            except:
                return
    except Exception:
        pass

    match c.data.split(':')[0]:
        case 'start_container':
            try:
                dckr.start(target)

                await bot.edit_message_text(
                    tds.get('menu_body').format(tds.get('state_on'), op.get_user(int(target), 'datumbis')) + f'\nID: {target}', 
                    reply_markup=get_running_menu(tds, target), inline_message_id=c.inline_message_id
                )
            except MessageNotModifiedError:
                pass
            except Exception as e:
                try:
                    await c.answer(re.sub(r'<.{1,4}>', '', tds.get('proc_err')))
                except:
                    return
                logging.error(e)
        case 'stop_container':
            try:
                dckr.stop(target)

                await bot.edit_message_text(
                    tds.get('menu_body').format(tds.get('state_off'), op.get_user(int(target), 'datumbis')) + f'\nID: {target}',
                    reply_markup=get_inactive_menu(tds, target), inline_message_id=c.inline_message_id
                )
            except MessageNotModifiedError:
                pass
            except Exception as e:
                try:
                    await c.answer(re.sub(r'<.{1,4}>', '', tds.get('proc_err')))
                except:
                    return
                logging.error(e)
        case _:
            try:
                await dckr.restart(target)

                await bot.edit_message_text(
                    tds.get('menu_body').format(tds.get('state_on'), op.get_user(int(target), 'datumbis')) + f'\nID: {target}',
                    reply_markup=get_running_menu(tds, target), inline_message_id=c.inline_message_id
                )
            except MessageNotModifiedError:
                pass
            except Exception as e:
                try:
                    await c.answer(re.sub(r'<.{1,4}>', '', tds.get('proc_err')))
                except:
                    return
                logging.error(e)
        
    try:
        await c.answer(re.sub(r'<.{1,4}>', '', tds.get('proc_done')))
    except:
        pass


@dp.callback_query_handler(
    lambda c: c.data.split(':')[0] in (
            'mock_start_container',
            'mock_stop_container',
            'mock_restart_container'
    )
)
async def mock_container_callback_handler(c: types.CallbackQuery):
    if butils.bignore(c.from_user):
        return

    data: dict = json.load(open('haupt.json', 'r', encoding='utf-8'))
    tds: TDS = TDS(c.from_user)
    if 'mocking_auth' not in data[str(c.from_user.id)].keys():
        try:
            return await c.answer(re.sub(r'<.{1,4}>', '', tds.get('proc_err')))
        except:
            return
    target = data[str(c.from_user.id)]['mocking_auth']['id']

    try:
        if target != c.data.split(':')[1]:
            try:
                return await c.answer(tds.get(f'notyourthing{random.randint(1, 4)}'))
            except:
                return
    except Exception:
        pass

    match c.data.split(':')[0]:
        case 'mock_start_container':
            try:
                dckr.start(target)

                await bot.edit_message_text(
                    f"⚫{tds.get('menu_body')[1:]}".format(tds.get('state_on'), op.get_user(int(target), 'datumbis')) + f'\nID: {target}', 
                    reply_markup=get_mock_running_menu(tds, target), inline_message_id=c.inline_message_id
                )
            except MessageNotModifiedError:
                pass
            except Exception as e:
                try:
                    return await c.answer(re.sub(r'<.{1,4}>', '', tds.get('proc_err')))
                except:
                    return
                logging.error(e)
        case 'mock_stop_container':
            try:
                dckr.stop(target)

                await bot.edit_message_text(
                    f"⚫{tds.get('menu_body')[1:]}".format(tds.get('state_off'), op.get_user(int(target), 'datumbis')) + f'\nID: {target}',
                    reply_markup=get_mock_inactive_menu(tds, target), inline_message_id=c.inline_message_id
                )
            except MessageNotModifiedError:
                pass
            except Exception as e:
                try:
                    return await c.answer(re.sub(r'<.{1,4}>', '', tds.get('proc_err')))
                except:
                    return
                logging.error(e)
        case _:
            try:
                await dckr.restart(target)

                await bot.edit_message_text(
                    tds.get('menu_body').format(tds.get('state_on'), op.get_user(int(target), 'datumbis')) + f'\nID: {target}',
                    reply_markup=get_mock_running_menu(tds, target), inline_message_id=c.inline_message_id
                )
            except MessageNotModifiedError:
                pass
            except Exception as e:
                try:
                    await c.answer(re.sub(r'<.{1,4}>', '', tds.get('proc_err')))
                except:
                    return
                logging.error(e)
        
    try:
        await c.answer(re.sub(r'<.{1,4}>', '', tds.get('proc_done')))
    except:
        return


async def suspend(m: types.Message) -> types.Message | None:
    """
        Wrapper for do_routine method of Verlangsamer with messages to violators as points of exit.
        :param m: Message.
        :return: Sent message.
    """
    lamr = await lam.do_routine(m.from_user)
    tram = TDS(m.from_user)
    if lamr[1] != 0:
        if lamr not in [4, 5]:
            return await m.reply(
                tram.get('floodwait_block_timed').format(f'{lamr[-1]} UTC')
            )
        elif lamr == 4:
            return await m.reply(
                tram.get('floodwait_block_lastwarning').format(
                    f'{lamr[-1]} UTC'
                )
            )
        elif lamr == 5:
            return await m.reply(tram.get('floodwait_block_forever'))
    return None


async def expire_check():
    """
        Checks for expired subscriptions.
        :return: None.
    """
    with open('haupt.json') as file:
        try:
            data: dict = json.load(file)
        except json.JSONDecodeError:
            print('Duck you')
    for user_id in data.keys():
        if butils.expire(user_id):
            await bot.send_message(
                user_id,
                TDS().get('expired', json.load(open('haupt.json', 'r', encoding='utf-8'))[str(user_id)]['lang'])
            )


async def mock_check():
    data = json.load(open('haupt.json', 'r', encoding='utf-8'))
    auth = json.load(open('auth.json', 'r', encoding='utf-8'))
    for user_id in data.keys():
        if 'mocking_auth' in data[user_id].keys():
            if data[user_id]['mocking_auth']['id'] not in auth.keys():
                del data[user_id]['mocking_auth']
                await bot.send_message(user_id, '⚫ <b>Connection to container with mocked credentials interrupted.</>')
            elif data[user_id]['mocking_auth']['basic_key'] != auth[data[user_id]['mocking_auth']['id']]['basic']: 
                del data[user_id]['mocking_auth']
                await bot.send_message(user_id, '⚫ <b>Connection to container with mocked credentials interrupted.</>')
    with open('haupt.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)     


async def warning_of_day_left() -> None:
    """
        Sends a warning to sthe user about the end of the subscription.
        :return: None.
    """
    data = json.load(open('haupt.json', 'r', encoding='utf-8'))
    for user_id in data.keys():
        if butils.if_day_left(user_id):
            try:
                await bot.send_message(
                    user_id,
                    TDS().get('one_day_left', data[user_id]['lang'], 'a').format(op.get_user(int(user_id), 'datumbis'))
                )
            except Exception as e:
                logging.error(e)


# Scheduling routine tasks of Verlangsamer.
async def got_scheduled():
    asch.every(10).seconds.do(lam.clear_routine)
    asch.every(8).seconds.do(lam.blocktime_is_out)
    asch.every(5).seconds.do(expire_check)
    asch.every(15).seconds.do(mock_check)
    asch.every(30).seconds.do(warning_of_day_left)
    while True:
        await asch.run_pending()
        await asyncio.sleep(2)


async def on_startup(_):
    asyncio.create_task(got_scheduled())


def form_commands_array(commands_dict: dict) -> list:
    """
        Forms a list of commands for bot.
        :param commands_dict: Dictionary of commands.
        :return: List of commands.
    """
    commands = []
    for command in commands_dict.keys():
        commands.append(types.BotCommand(command, commands_dict[command]))
    return commands


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
