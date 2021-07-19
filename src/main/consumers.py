""" Main consumer """

import json
import datetime
from main.models import Reminders
from channels.generic.websocket import WebsocketConsumer

class ReminderConsumer(WebsocketConsumer):
    """ Обрабатывает запросы (WebSocket) """
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data: dict):
        """ Принятие запросов """
        text_data_json = json.loads(text_data)
        type = text_data_json['type']

        # Первое подключение
        if type == 'initialization':
            data = get_initialization_data()

        # Удаление Remind
        if type == 'removeRemind':
            remindId = text_data_json['remindId'].replace('remind_', '')
            data = remove_remind(remindId)

        # Изменение Remind
        if type == 'editRemind':
            remindNewData = text_data_json['remindNewData']
            data = edit_remind(remindNewData)

        # Добавление нового Remind
        if type == 'newRemind':
            newRemindData = text_data_json['newRemindData']
            data = add_new_remind(newRemindData)

        # Отправляем ответ
        self.send(text_data=json.dumps({
            'data': data
        }))


def get_initialization_data() -> dict:
    """ Показ всех Reminds """
    try:
        objects = Reminders.objects.order_by('date', 'time')
        
        data = {
            'type': 'initialization',
            'status': 'success',
            'data': []
        }
        for index, remind in enumerate(objects):
            date = remind.date.strftime('%Y-%m-%d').split('-')
            date[1] = str(int(date[1]) - 1).zfill(2) # Т.к. в JS месяц начинается с 0
            time = remind.time.strftime('%H-%M').split('-')
            
            data['data'].append(
                {
                    'id': 'remind_' + str(remind.id),
                    'title': remind.title,
                    'date': {
                        'year': date[0],
                        'month': date[1],
                        'day': date[2] 
                    },
                    'time': {
                        'hour': time[0],
                        'minute': time[1]
                    }
                }
            )
    except:
        data = {
            'type': 'initialization',
            'status': 'fail'
        }

    return data

def remove_remind(id: str) -> dict:
    """ Функция, удаляющая выбраный Remind """
    try:
        remind = Reminders.objects.get(id = id)
        remind.delete()

        data = {
            'type': 'removeRemind',
            'status': 'success'
        }
    except:
        data = {
            'type': 'removeRemind',
            'status': 'fail'
        }

    return data

def edit_remind(remindNewData: object) -> dict:
    """ Функция, изменяющая данные выбраного Remind """
    try:
        remindId = int(remindNewData['id'].replace('remind_', ''))
        title = remindNewData['title']

        date = get_date(remindNewData['date'])
        time = get_time(remindNewData['time'])

        remind = Reminders.objects.get(id = remindId)
        remind.title = title
        remind.date = date
        remind.time = time
        remind.save()

        data = {
            "type": "editRemind",
            "status": "success"
        }
    except:
        data = {
            "type": "editRemind",
            "status": "fail"
        }
    
    return data

def add_new_remind(newRemindData: object) -> dict:
    """ Функция, добавляющая новый Remind """
    try:
        title = newRemindData['title']

        date = get_date(newRemindData['date'])
        time = get_time(newRemindData['time'])

        newRemind = Reminders()
        newRemind.title = title
        newRemind.date = date
        newRemind.time = time
        newRemind.save()

        data = {
            'type': 'newRemind',
            'status': 'success',
            'data': {
                'id': 'remind_' + str(newRemind.id),
            }
        }
    except:
        data = {
            'type': 'newRemind',
            'status': 'fail'
        }

    return data

def get_date(remindDate: object()) -> datetime:
    # month + 1, т.к. в JS месяц начинается с 0 
    date = datetime.date(int(remindDate['year']), int(remindDate['month']) + 1, int(remindDate['day']))
    return date

def get_time(remindTime: object()) -> datetime:
    time = datetime.time(int(remindTime['hour']), int(remindTime['minute']))
    return time
