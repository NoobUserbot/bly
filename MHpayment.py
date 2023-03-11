# miya.host payment management utilities
import random
from datetime import datetime, timedelta, timezone
import logging
from logging.handlers import TimedRotatingFileHandler
from json import JSONDecodeError, load, dump
from string import ascii_letters
from datetime import datetime, timedelta

import requests
import yoomoney as YM
from yoomoney.exceptions import YooMoneyError

from utilities.tokens import *
import MHoperator as op


# Logger setup
logger = logging.getLogger('miya.host')
logger.setLevel(logging.ERROR)
handler = TimedRotatingFileHandler('logs/miya.host.log', when='midnight', backupCount=100)
handler.setLevel(logging.ERROR)
handler.setFormatter(
    logging.Formatter('[%(asctime)s] [%(levelname)s] "%(message)s" - %(name)s')
)
logger.addHandler(handler)


def update_length(length: int, recipient: int, type: str = 'incr'):
    """Updates subscription length.

    :param length: Length to add or subtract
    :param recipient: User ID
    :param type: Increase/Decrease
    :return: New expiration date or False, if failed.
    """
    if not op.get_user(recipient):
        op.create_user(recipient)
    if type == 'incr':
        nowth = op.get_user(recipient, 'datumbis')
        if not nowth or datetime.strptime(nowth, '%H:%M:%S, %d.%m.%Y') < datetime.now():
            exp = datetime.now(tz=timezone(timedelta(hours=3))) + timedelta(days=length)
        else:
            exp = datetime.strptime(nowth, '%H:%M:%S, %d.%m.%Y') + timedelta(days=length)
        op.edit_user(recipient, 'datumbis', exp.strftime('%H:%M:%S, %d.%m.%Y'))
        return exp.strftime('%H:%M:%S, %d.%m.%Y')
    elif type == 'decr':
        nowth = op.get_user(recipient, 'datumbis')
        if not nowth or datetime.strptime(nowth, '%H:%M:%S, %d.%m.%Y') < datetime.now():
            return False
        else:
            exp = datetime.strptime(nowth, '%H:%M:%S, %d.%m.%Y') - timedelta(days=length)
        op.edit_user(recipient, 'datumbis', exp.strftime('%H:%M:%S, %d.%m.%Y'))
        return exp.strftime('%H:%M:%S, %d.%m.%Y')
    else:
        return False


def create_invoice(platform: str = 'q',
                   recipient: int = 0, amount: float = op.equelle("price"),
                   comment: str = '',
                   cc: str = '') -> str:
    """Creates invoice for user.

    :param platform: First lowercase letter of the name of platform
    :param recipient: User ID
    :param amount: Amount to pay
    :param comment: Comment to invoice
    :return: Invoice ID or False, if failed.
    """
    match platform:
        case 'q':
            return _create_qiwi_invoice(recipient, amount, comment)
        case 'y':
            return _create_yoomoney_invoice(recipient, amount, comment)
        case 'c':
            return _create_crypto_invoice(recipient, amount, cc, comment)
        case _:
            return 'Ах ты, пидорас! Я не знаю такой платёжной системы!'


def _create_qiwi_invoice(recipient: int, amount: float, comment: str) -> str:
    if not comment:
        comment = f'miya.host subscription for {recipient}'
    else:
        comment = str(comment)

    response: requests.Response = requests.put(
        'https://api.qiwi.com/partner/bill/v1/bills/'
        f'{"".join(random.choices(ascii_letters, k=25))}',
        headers={
            "Accept": 'application/json',
            "Content-Type": 'application/json',
            "Authorization": f'Bearer {prt}'
        },
        json={
            "amount": {
                "value": round(amount, 2),
                "currency": 'RUB'
            },
            "expirationDateTime": (datetime.now(tz=timezone(timedelta(hours=3))) + timedelta(minutes=15)).isoformat().split('.', 1)[0] + '+03:00',
            "comment": comment,
        }
    )
    if response.ok:
        try:
            return response.json().get('payUrl', '')
        except JSONDecodeError:
            logger.error(f'Failed to decode JSON: {response.text}')
    else:
        logger.error(f'Failed to create invoice ({response.status_code}): {response.text}')

    return ''


def _get_crypto_exr(cci: str) -> float:
    """
    Get exchange rate of current subscription price in crypto currency.
    :param cci: Crypto currency name
    :return: Exchange rate
    """
    ccis = ['BTC', 'TON', 'ETH', 'USDT', 'USDC', 'BUSD']
    amount = op.equelle("price")
    if cci not in ccis:
        return 'Ах ты, пидорас! Я не знаю такой криптовалюты!'
    headers = {
        'Host': 'pay.crypt.bot',
        'Crypto-Pay-API-Token': cryptotok
    }
    cryptos = requests.get('https://pay.crypt.bot/api/getExchangeRates/', headers = headers)
    dictionary = cryptos.json()['result']
    to_r_er: dict
    crypto = cci
    for i in dictionary:
        if i['source'] == crypto and i['target'] == 'RUB':
            to_r_er = i
            break
    if not to_r_er:
        return 'Курс не нашёлся :('
    
    return round(amount / float(to_r_er['rate']), 16)



def _create_crypto_invoice(recipient: int, amount: float, cryptocurrency: str, comment: str) -> str:
    """
    Creates crypto invoice for user.
    :param recipient: User ID
    :param amount: Amount to pay
    :param cryptocurrency: Crypto currency name
    :param comment: Comment to invoice
    :return: Invoice ID or False, if failed.
    """
    if not comment:
        comment = f'miya.host subscription for {recipient}'
    ccis = ['BTC', 'TON', 'ETH', 'USDT', 'USDC', 'BUSD']
    if cryptocurrency not in ccis:
        return 'Ах ты, пидорас! Я не знаю такой криптовалюты!'
    headers = {
        'Host': 'pay.crypt.bot',
        'Crypto-Pay-API-Token': cryptotok
    }
    params = {
        'asset': cryptocurrency,
        'amount': amount,
        'description': 'Pay this invoice to access miyahost functions for a month.',
        'hidden_message': 'Thanks for your payment! Come back to bot and press a button to check your payment status.',
        'paid_btn_name': 'openBot',
        'paid_btn_url': 'https://t.me/miyahostbot',
        'payload': comment,
        'allow_anonymous': False,
        'expires_in': 900
    }
    req = requests.get('https://pay.crypt.bot/api/createInvoice/', headers=headers, params=params)
    if req.ok:
        return req.json()['result']['pay_url']
    else:
        return False


def _create_yoomoney_invoice(recipient: int, amount: float, comment: str) -> str:
    if not comment:
        comment = f'miya.host subscription for {recipient}'
    else:
        comment = str(comment)

    paym = YM.Quickpay('4100118021186932', 'shop', 'Buy subscription for miyahost', 'SB', amount, label=comment)
    return paym.redirected_url


def check_payment(recipient: int, platform: str = 'q') -> bool:
    """Creates invoice for user

    :param platform: First lowercase letter of the name of platform
    :param recipient: User ID
    :return: Was the payment successful or not
    """
    if recipient in load(open('anderequelle.json'))['admins']:
        return True
    match platform:
        case 'q':
            return _check_qiwi_payment(recipient)
        case 'y':
            return _check_yoomoney_payment(recipient)
        case 'c':
            return _check_crypto_payment(recipient)
        case _:
            return False


def _check_yoomoney_payment(recipient: int) -> bool:
    try:
        client = YM.Client(ymtoken)
        history = client.operation_history(label=f'miya.host subscription for {recipient}')
    except YooMoneyError as e:
        logger.critical(f'YooMoneyError: {e} ({recipient})')
        return False
    
    op_cdb = load(open('bezahl.json', 'r', encoding='utf-8'))

    for operation in history.operations:
        if operation.status == "success" and operation.operation_id not in op_cdb['ympast']:
            op_cdb['ympast'].append(operation.operation_id)
            dump(op_cdb, open('bezahl.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
            return True
        else:
            return False
    return False


def _check_qiwi_payment(recipient: int) -> bool:
    response: requests.Response = requests.get(
        'https://edge.qiwi.com/payment-history/v2/persons/79282446414/payments',
        headers={
            "Accept": 'application/json',
            "Content-Type": 'application/json',
            "Authorization": f'Bearer {tok1}'
        },
        params={
            "rows": 3,
            "operation": 'IN',
            "sources": 'QW_RUB'
        }
    )

    if response.ok:
        op_cdb = load(open('bezahl.json', 'r', encoding='utf-8'))
        try:
            for payment in response.json().get('data', []):
                if payment.get('comment', '') == f'miya.host subscription for {recipient}' and payment.get('txnId', '') not in op_cdb['qvpast']:
                    op_cdb['qvpast'].append(payment.get('txnId', ''))
                    dump(op_cdb, open('bezahl.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
                    return True
        except JSONDecodeError:
            logger.critical(f'JSONDecodeError while checking payment for {recipient}, {response.text}')
    else:
        logger.critical(f'HTTPError while checking payment: {response.status_code} ({recipient}), {response.text}')

    return False


def _check_crypto_payment(recipient: int, amount: int = 50) -> bool:
    """
    Check crypto invoice.
    :param recipient: User ID
    :param amount: Amount of invoices to be returned
    :return: True if invoice is paid, False if not
    """

    headers = {
        'Host': 'pay.crypt.bot',
        'Crypto-Pay-API-Token': cryptotok,
    }
    params = {
        'count': amount
    }
    req = requests.get('https://pay.crypt.bot/api/getInvoices/', headers=headers, params=params)
    results = req.json()['result']['items']
    for r in results:
        if r['payload'] == f'miya.host subscription for {recipient}':
            if r['status'] == 'paid':
                op_cdb = load(open('bezahl.json', 'r', encoding='utf-8'))
                if r['invoice_id'] not in op_cdb['cbpast']:
                    op_cdb['cbpast'].append(r['invoice_id'])
                    dump(op_cdb, open('bezahl.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
                else:
                    return False
                return True
            else:
                return False
