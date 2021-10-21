import requests
import json
import re
from classes import Tariff
from classes import Hall
from classes import Problem


STATE_REQUEST_KEY = 'session'
STATE_RESPONSE_KEY = 'session_state'

API_MAP_KEY = 'insert_your_key'

def welcome_message(event):
    text = ('Привет! Это метро Санкт-Петербурга. '
'Я могу подсказать информацию о станции или помочь с билетами. '
'С чем нужно помочь?')
    return make_response(text, buttons=[
        button('Билеты', hide=True),
        button('Станции', hide=True),
    ])

def make_response(text, state=None, buttons=None):
    response = {
        'text': text,
    }
    webhook_response = {
        'response': response,
        'version': '1.0',
    }
    if state is not None:
        webhook_response[STATE_RESPONSE_KEY] = state
    if buttons is not None:
        response['buttons'] = buttons
    return webhook_response

def what(event):
    text = 'Для получения информации по билетам скажите "Билеты".\n Для получения информации по станциям скажите "Станции".\n Также вы можете использовать конкретные запросы в любой момент, к примеру:\n - Режим работы станции Автово\n - Информация по ближайшей станции\n - Ограничения на станции Рыбацкое\n - Тарифы на студенческий билет\n - Найди точки продаж билетов\n'
    return make_response(text, 
    buttons=[
        button('Билеты', hide=True),
        button('Станции', hide=True),
        button('Режим работы станции Автово', hide=True),
        button('Информация по ближайшей станции', hide=True),
        button('Ограничения на станции Рыбацкое', hide=True),
        button('Тарифы на студенческий билет', hide=True),
        button('Найди точки продаж билетов', hide=True),
    ])

def fallback(event):
    state=event['state'][STATE_REQUEST_KEY]
    state['fallback']='1'
    return make_response(
        'Извините, я вас не поняла. Попробуйте переформулировать фразу и сказать её чётко.', 
        state, buttons=[
            button('Билеты', hide=True),
            button('Станции', hide=True),
            button('Помощь', hide=True),
        ])

def fallback_gide(event):
    state=event['state'][STATE_REQUEST_KEY]
    state['fallback']='2'
    return make_response(
        'Кажется я так не умею, но я могу дать информацию о станции по её названию или же рассказать о тарифах на проезд.', 
        state, buttons=[
            button('Билеты', hide=True),
            button('Станции', hide=True),
            button('Помощь', hide=True),
        ])

def fallback_exit(event):
    state=event['state'][STATE_REQUEST_KEY]
    state['fallback']='3'
    return make_response(
        'Видимо у меня нет того что вам нужно. Можем попробовать ещё раз или закрыть навык?', 
        state, buttons=[
            button('Ещё раз', hide=True),
            button('Хватит', hide=True),
            button('Помощь', hide=True),
        ])

def no_fallback(event):
    return make_response(
        'Хорошо. Чем я могу помочь?',
        buttons=[
            button('Билеты', hide=True),
            button('Станции', hide=True),
            button('Что ты умеешь?', hide=True),
        ])

def handler(event, context):
    intents = event['request'].get('nlu',{}).get('intents', {})
    state = event.get('state').get(STATE_REQUEST_KEY,{})
    if event['session']['new']:
        return welcome_message(event)
    elif 'info_stations' in intents:
        return info_stations(event)
    elif 'info_one_station' in intents:
        return info_one_station(event)
    elif 'about_time_station' in intents:
        return about_time_station(event)
    elif 'about_time_no_name_station' in intents and (state.get('screen')=='info_one_station' or state.get('screen')=='search_metro_with_address' or state.get('screen')=='problems_station' or state.get('screen')=='about_time_station'):
        return about_time_station(event, state.get('name_station').lower())
    elif 'problems_station' in intents:
        return problems_station(event)
    elif 'problems_no_name_station' in intents and (state.get('screen')=='info_one_station' or state.get('screen')=='search_metro_with_address' or state.get('screen')=='about_time_station' or state.get('screen')=='problems_station'):
        return problems_station(event, state.get('name_station').lower())
    elif 'about_nearest_station' in intents:
        return about_nearest_station(event)
    elif state.get('screen')=='about_nearest_station':
        return search_metro_with_address(event)
    elif 'yes' in intents and state.get('screen')=='search_metro_with_address' and state.get('error')=='1':
        return about_nearest_station(event)


    elif 'tickets_and_sale' in intents:
        return tickets_and_sale(event)
    elif 'tariffs' in intents:
        return tariffs(event)
    elif 'about_tariff' in intents:
        return about_tariff(event)
    elif 'yes' in intents and state.get('screen')=='about_tariff':
        return about_tariff_more(event, state.get('typeTariff'),)
    elif 'yes' in intents and state.get('screen')=='about_tariff_more':
        return about_tariff_more(event, state.get('typeTariff'),)
    elif 'no' in intents:
        return no_fallback(event)

    elif 'points_of_sale' in intents:
        return points_of_sale(event)
    

    elif 'what' in intents:
        return what(event)
    elif state.get('fallback')=='1':
        return fallback_gide(event)
    elif state.get('fallback')=='2':
        return fallback_exit(event)
    else:
        return fallback(event)

def button(title, payload=None, url=None, hide=True):
    button = {
        'title': title,
        'hide': hide,
    }
    if payload is not None:
        button['payload'] = payload
    if url is not None:
        button['url'] = url
    return button

def info_stations(event):
    text = 'Можете назвать конкретную станцию. Или мне поискать ближайшую?'
    return make_response(text, buttons=[
        button('Ближайшая станция', hide=True),
        button('Не нужно', hide=True),
    ], state={
        'screen': 'info_stations',
    })

def info_one_station(event):
    intent = event['request']['nlu']['intents']['info_one_station']
    nameStation = intent['slots']['station']['value']
    text='Я могу подсказать режим работы данной станции или ограничения на ней. Что вас интересует?'
    return make_response(text, buttons=[
        button('Режим работы станции', hide=True),
        button('Ограничения на станции', hide=True),
        button('Не нужно', hide=True),
    ], state={
        'screen': 'info_one_station',
        'name_station': nameStation,
    })
    
def about_time_station(event, nameStation=''):
    if nameStation=='':
        intent = event['request']['nlu']['intents']['about_time_station']
        nameStation = intent['slots']['station']['value']
    with open('data_stations_time.json') as f:
        data = json.load(f)
    if not(data == None):
        text = ''
        listHalls = sorted_list_halls(nameStation, data)
        if len(listHalls)==0:
            text = 'Не нашла информации по данной станции. Попробуйте ещё раз.'
            return make_response(text, state={
                'screen': 'about_time_station',
                }, buttons=[
                    button('Тарифы', hide=True),
                    button('Станции', hide=True),
                    ])
        else:
            text=''
            for hall in listHalls:
                text+=hall.display_info()
            text+='Чем ещё я могу помочь?'
            return make_response(text, state={
                'screen': 'about_time_station',
                'name_station': nameStation,
                }, buttons=[
                    button('Тарифы', hide=True),
                    button('Станции', hide=True),
                    button('Ограничения данной станции', hide=True),
                    ])
    else:
        text = 'Пока информация по станции мне не доступна. Рассказать про другие станции или подсказать тарифы?'
    return make_response(text, state={
        'screen': 'about_time_station',
    }, buttons=[
        button('Тарифы', hide=True),
        button('Станции', hide=True),
    ])

def problems_station(event, nameStation=''):
    if nameStation=='':
        intent = event['request']['nlu']['intents']['problems_station']
        nameStation = intent['slots']['station']['value']
    with open('data_problems.json') as f:
        data = json.load(f)
    if not(data == None):
        text = ''
        listProblems = sorted_list_problems(nameStation, data)
        if len(listProblems)==0:
            text = 'Не нашла ограничений по данной станции. С чем ещё помочь?'
            return make_response(text, state={
                'screen': 'problems_station',
                'name_station': nameStation,
                }, buttons=[
                    button('Тарифы', hide=True),
                    button('Станции', hide=True),
                    button('Режим работы данной станции', hide=True),
                    ])
        else:
            text=''
            for problem in listProblems:
                text+=problem.display_info()
            text+='Чем ещё я могу помочь?'
            return make_response(text, state={
                'screen': 'problems_station',
                'name_station': nameStation,
                }, buttons=[
                    button('Тарифы', hide=True),
                    button('Станции', hide=True),
                    button('Режим работы данной станции', hide=True),
                    ])
    else:
        text = 'Пока информация по станции мне не доступна. Рассказать про другие станции или подсказать тарифы?'
    return make_response(text, state={
        'screen': 'problems_station',
    }, buttons=[
        button('Тарифы', hide=True),
        button('Станции', hide=True),
    ])

def sorted_list_halls(nameStation, data):
    listHalls = []
    for value in data:
        if nameStation in value['row']['name_hall'].lower():
            if 'закрыт' in value['row']['time_open'].lower():
                hall = Hall(value['row']['name_hall'], value['row']['time_open'], value['row']['time_close_input'], value['row']['time_close_exit'], True)
                listHalls.append(hall)
            else:
                hall = Hall(value['row']['name_hall'], value['row']['time_open'], value['row']['time_close_input'], value['row']['time_close_exit'], False)
                listHalls.append(hall)
    return listHalls

def sorted_list_problems(nameStation, data):
    listProblems = []
    for value in data:
        if nameStation in value['row']['name_hall'].lower():
            problem = Problem(value['row']['name_hall'], value['row']['number_line'], value['row']['restrictions'], value['row']['type_days'], value['row']['date_finish'])
            listProblems.append(problem)
    return listProblems

def about_nearest_station(event):
    text = 'Назовите адрес, где вы находитесь.'
    return make_response(text, state={
        'screen': 'about_nearest_station',
    })

def search_metro_with_address(event):
    url = 'https://geocode-maps.yandex.ru/1.x/'
    payload = {
    'apikey': API_MAP_KEY, 
    'geocode': 'Россия+Северо-Западный федеральный округ+Санкт-Петербург+'+event['request']['command'],
    'format': 'json'}  
    response = requests.get(url, params=payload)
    data = json.loads(response.text) 
    if response or (data == response.json()) or not (data == None):
        if data['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found'] == 0:
            text = 'Что-то не получается найти это место. Попробуем ещё раз?'
            return make_response(text, state={'screen': 'search_metro_with_address', 'error': '1'})
        if data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['precision'] == 'exact':
            location = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
            payload['geocode'] = location
            payload['kind'] = 'metro'
            payload['result'] = 1
            response = requests.get(url, params=payload)
            data = json.loads(response.text) 
            if data['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found'] == 0:
                text = 'Не вижу поблизости станций метро. Укажите другой адрес. Попробуем ещё раз?'
                return make_response(text, state={'screen': 'search_metro_with_address', 'error': '1'})
            nameMetro = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['name']
            text = 'Ближайшая к вам станция ' + nameMetro + '.' + '\n' + 'Подсказать режим работы станции или ограничения на ней?'
        else:
            text = 'Не могу определить точный адрес. Сообщите название улицы и номер дома. Попробуем ещё раз?'
            return make_response(text, 
            state={'screen': 'search_metro_with_address', 'error':'1'}, 
            buttons=[button('Нет', hide=True), button('Да', hide=True)])
    return make_response(text, state={
        'screen': 'search_metro_with_address',
        'error': '0',
        'name_station': nameMetro[6:],
    },buttons=[
        button('Режим работы станции', hide=True),
        button('Ограничения на станции', hide=True),
        button('Нет', hide=True),
    ])

def tickets_and_sale(event):
    text = 'Хотите узнать тарифы или найти точку продаж билетов?'
    return make_response(text, buttons=[
        button('Тарифы', hide=True),
        button('Точки продаж', hide=True),
        button('Нет', hide=True),
    ])

def tariffs(event):
    text = 'Я нашла различные виды проездных билетов. Подорожник, студенческий, ученический, пенсионный. По какому билету подсказать тарифы? '
    return make_response(text, buttons=[
        button('Подорожник', hide=True),
        button('Cтуденческий', hide=True),
        button('Ученический', hide=True),
        button('Пенсионный', hide=True),
        button('Не нужно', hide=True),
    ])

def about_tariff(event):
    intent = event['request']['nlu']['intents']['about_tariff']
    typeTariff = intent['slots']['type']['value']
    with open('data_tariff.json') as f:
        data = json.load(f)
    if not(data == None):
        text = ''
        listTariff = sorted_list(typeTariff, data)
        if len(listTariff)==2:
            text = 'Нашла два тарифа. ' + listTariff[0].display_info() + listTariff[1].display_info() + 'Рассказать про тарифы других билетов ещё или подсказать информацию по станции?'
            return make_response(text, state={
                'screen': 'about_tariff',
                'typeTariff': typeTariff,
                }, buttons=[
                    button('Тарифы', hide=True),
                    button('Станции', hide=True),
                    ])
        elif len(listTariff)>1:
            text = 'Самый дешёвый. ' + listTariff[0].display_info() + 'Но есть подороже, рассказать про них?'
            return make_response(text, state={
                'screen': 'about_tariff',
                'typeTariff': typeTariff,
                }, buttons=[
                    button('Нет', hide=True),
                    button('Да', hide=True),
                    ])
        else:
            text = 'Нашла один билет. ' + listTariff[0].display_info() + 'Рассказать про тарифы других билетов ещё или подсказать информацию по станции?'
            return make_response(text, state={
                'screen': 'about_tariff',
                'typeTariff': typeTariff,
                }, buttons=[
                    button('Тарифы', hide=True),
                    button('Станции', hide=True),
                    ])
    else:
        text = 'Пока информация по тарифам для данного типа билета мне не доступна. Рассказать про тарифы других билетов или подсказать информацию по станции?'
    return make_response(text, state={
        'screen': 'about_tariff',
        'typeTariff': typeTariff,
    }, buttons=[
        button('Тарифы', hide=True),
        button('Станции', hide=True),
                            button('Ограничения данной станции', hide=True),
    ])

def about_tariff_more(event, typeTariff):
    state = event.get('state').get(STATE_REQUEST_KEY,{})
    with open('data_tariff.json') as f:
        data = json.load(f)
    listTariff = sorted_list(typeTariff, data)
    if state.get('last')=='yes':
        index=state.get('index')
        text = listTariff[index].display_info() + 'Это последний тариф, который я нашла.'
        return make_response(text, state={
            'screen': 'about_tariff_more',
        }, buttons=[
            button('Билеты', hide=True),
            button('Станции', hide=True),
        ])
    elif state.get('index') is not None :
        index=state.get('index')
    else:
        index=1
    text = ''
    i=1
    while i<3:
        text += listTariff[index].display_info()
        index+=1
        i+=1
    if len(listTariff)-index==1:
        text += 'Есть ещё один тариф, рассказать о нём?'
        return make_response(text, state={
            'screen': 'about_tariff_more',
            'typeTariff': typeTariff,
            'index': index,
            'last': 'yes',
        }, buttons=[
            button('Нет', hide=True),
            button('Да', hide=True),
        ])
    if len(listTariff)-index>1:
        text += 'Есть ещё несколько тарифов, рассказать?'
        return make_response(text, state={
            'screen': 'about_tariff_more',
            'typeTariff': typeTariff,
            'index': index,
        }, buttons=[
            button('Нет', hide=True),
            button('Да', hide=True),
        ])
    if len(listTariff)-index==0:
        text += 'Это последние тарифы, которые я нашла.'
        return make_response(text, state={
            'screen': 'about_tariff_more',
        }, buttons=[
            button('Билеты', hide=True),
            button('Станции', hide=True),
        ])

def sorted_list(typeTariff, data):
    listTariff = []
    if typeTariff=='student':
        text = 'Студенческий, ISIC'
    elif typeTariff=='school':
        text = 'Ученический'
    elif typeTariff=='plantain':
        text = 'Подорожник'
    elif typeTariff=='retiree':
        text = 'ЕИЛБ (пенсионный)'
    for value in data:
        if value['row']['type']==text:
            tariff = Tariff(value['row']['type_of_ticket'], value['row']['cost'])
            listTariff.append(tariff)
    listTariff.sort(key=lambda tariff: int(tariff.cost))
    return listTariff

def points_of_sale(event):
    text = 'Приобрести билеты можно на любой станции метро. Дополнительные точки продаж билетов отобразила на карте.'
    return make_response(text, buttons=[
        button('Открыть карту точек продаж', hide=False, url='https://yandex.ru/maps/?ll=30.316362,59.927458&spn=0.16,0.16&text=Санкт-Петербургское+государственное+казенное+учреждение+Организатор+перевозок'),
        button('Открыть сайт карты "Подорожник"', hide=False, url='http://podorozhnik.spb.ru/'),
        button('Открыть сайт карты учащегося/студента/пенсионера', hide=False, url='https://zakaz.ltkarta.ru/'),
        button('Станции', hide=True),
        button('Нет', hide=True),
    ])