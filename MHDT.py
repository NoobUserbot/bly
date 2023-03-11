import requests, json 

def _get_crypto_exr(cci: str) -> float:
    """
    Get exchange rate of current subscription price in crypto currency.
    :param cci: Crypto currency name
    :return: Exchange rate
    """
    ccis = ['BTC', 'TON', 'ETH', 'USDT', 'USDC', 'BUSD']
    amount = 50
    if cci not in ccis:
        return 'Ах ты, пидорас! Я не знаю такой криптовалюты!'
    headers = {
        'Host': 'pay.crypt.bot',
        'Crypto-Pay-API-Token': '81898:AAXRFbXSOXy7foJXBfbvbf8Zr6Z51FRDctE'
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
    
    print(to_r_er)
    
    return amount / float(to_r_er['rate'])

def _check_crypto_invoice(recipient: int, amount: int = 50) -> bool:
    """
    Check crypto invoice.
    :param recipient: User ID
    :param amount: Amount of invoices to be returned
    :return: True if invoice is paid, False if not
    """

    headers = {
        'Host': 'pay.crypt.bot',
        'Crypto-Pay-API-Token': '81898:AAXRFbXSOXy7foJXBfbvbf8Zr6Z51FRDctE'
    }
    params = {
        'count': amount
    }
    req = requests.get('https://pay.crypt.bot/api/getInvoices/', headers=headers, params=params)
    results = req.json()['result']['items']
    for r in results:
        if r['payload'] == f'miya.host subscription for {recipient}':
            if r['status'] == 'paid':
                op_cdb = json.load(open('bezahl.json', 'r', encoding='utf-8'))
                if r['invoice_id'] not in op_cdb['cbpast']:
                    op_cdb['cbpast'].append(r['invoice_id'])
                    json.dump(op_cdb, open('bezahl.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
                else:
                    return False
                return True
            else:
                return False

# print(_check_crypto_invoice(1, _get_crypto_exr('USDT'), 'USDT', 'test'))

headers = {
        'Host': 'pay.crypt.bot',
        'Crypto-Pay-API-Token': '81898:AAXRFbXSOXy7foJXBfbvbf8Zr6Z51FRDctE'
    }
params = {
    'count': 50
}
req = requests.get('https://pay.crypt.bot/api/getInvoices/', headers=headers, params=params)
results = req.json()['result']['items']
print(results)
