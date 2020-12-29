# ВЕРСИЯ 4
import json
import requests
import hashlib
import time
import pprint


url = 'https://api.direct.yandex.ru/live/v4/json/'
SubClients = ['yamaguchi-adv', 'us-medica-adv', 'yamaguchi-axiom-adv', 'us-medica-region', 'yamaguchi-russia2017', 'Anatomico-Fujiiryoki']
with open('C:/users/934/PycharmProjects/key/Yandex_token.json') as f:
    data = json.load(f)

def dict_acc_sum(): # Получаем суммы(доступные для перевода) на счетах аккаунтов
    token = data['token']
    params = {'method': 'AccountManagement',
            'token': token,
            'locale': 'ru',
            "param": {"Action": 'Get',
                      "SelectionCriteria": {
                          "Logins": SubClients
                      }}}
    jparams = json.dumps(params, ensure_ascii=False).encode('utf8')
    response = requests.post(url, jparams).json()
    acc_name_dict = {i['Login']: [i['AccountID'], float(i['AmountAvailableForTransfer'])] for i in response['data']['Accounts']}
    return acc_name_dict


def TransferMoney(fromAcc, toAcc, amount, num):
    token = data['token']
    masterToken = data['masterToken']
    operationNum = num  # 7 Всегда добавляем +1
    usedMethod = 'AccountManagement'
    action = 'TransferMoney'
    login = 'osipov-yamaguchi'

    fin_string = (masterToken + str(operationNum) + usedMethod + action + login).encode('utf-8')
    fin_token = hashlib.sha256(fin_string).hexdigest()

    params = {
        'token': token,
        'locale': 'ru',
        "method": usedMethod,
        'finance_token': fin_token,
        "operation_num": operationNum,
        "param": {
            "Action": 'TransferMoney',
            "Transfers": [{"FromAccountID": fromAcc,
                           "ToAccountID": toAcc,
                           "Amount": amount,
                           "Currency": 'RUB'}]}}

    response = requests.post(url, data=json.dumps(params, ensure_ascii=False).encode('utf8'))
    print(response.text)

def main():
    data = dict_acc_sum()
    for key, items in data.items():
        print(key, items)

    TransferMoney(data['yamaguchi-adv'][0], data['us-medica-adv'][0], data['yamaguchi-adv'][1]*0.09, 17)
    time.sleep(30)
    TransferMoney(data['yamaguchi-adv'][0], data['us-medica-region'][0], data['yamaguchi-adv'][1]*0.11, 18)

    # TransferMoney(data['yamaguchi-russia2017'][0], data['us-medica-region'][0], data['yamaguchi-russia2017'][1]*0.5, 12)
    # time.sleep(30)
    # TransferMoney(data['Anatomico-Fujiiryoki'][0], data['us-medica-region'][0], data['Anatomico-Fujiiryoki'][1]*0.5, 13)
    # time.sleep(30)
    #TransferMoney(data['yamaguchi-axiom-adv'][0], data['us-medica-region'][0], data['yamaguchi-axiom-adv'][1]*0.5, 14)

main()