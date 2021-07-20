""" Main consumer """

import json
import datetime
from typing import Any
from main.models import Reminders
from django.core.mail import send_mail
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

        # Проверка изменений (раз в 5 минут)
        if type == 'checkReminderTimer':
            data = check_reminder_timer()

            # Если сейчас должен сработать Reminder
            if data:
                try:
                    send_mail('Reminders!', "New Reminder's finished - check it out", "Reminders", ['reminders.reminders1@gmail.com'], fail_silently=True)
                except:
                    pass
            else:
                return

        # Отправляем ответ
        self.send(text_data=json.dumps({
            'data': data
        }))

def check_reminder_timer() -> Any:
    try:
        data = None

        # Ближайщий Remind
        nearest_remind = Reminders.objects.order_by('date', 'time')[0]

        remind_date = nearest_remind.date
        current_date = datetime.date.today()

        # Если дата совпадает
        if (remind_date == current_date):
            remind_time = nearest_remind.time.strftime('%H:%M')
            current_time = datetime.datetime.now().strftime('%H:%M')

            # Если время совпадает
            if remind_time == current_time:
                # Удалим Remind
                nearest_remind_id = nearest_remind.id
                nearest_remind.delete()

                data = {
                    'type': 'timerRemoveRemind',
                    'status': 'success',
                    'data': {
                        'id': 'remind_' + str(nearest_remind_id),
                    }
                }
    except:
        data = None
    
    return data


def get_initialization_data() -> dict:
    """ Показ всех Reminds """
    try:
        remove_finished_reminders()

        objects = Reminders.objects.order_by('date', 'time')
        
        data = {
            'type': 'initialization',
            'status': 'success',
            'data': []
        }

        for remind in objects:
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

def remove_finished_reminders():
    """ Удаляет из БД уже законченные Reminders """
    try:
        objects = Reminders.objects.order_by('date', 'time')

        for remind in objects:
            remind_date = list(map(int, remind.date.strftime('%Y-%m-%d').split('-')))
            remind_time = list(map(int, remind.time.strftime('%H-%M').split('-')))

            # Получим дату и время выбранного Reminder
            remind_date_time = datetime.datetime(
                remind_date[0], remind_date[1], remind_date[2], remind_time[0], remind_time[1]
            )

            # Если Reminder уже в прошлом, то удалим
            if (remind_date_time <= datetime.datetime.now()):
                remind.delete()
            else:
                break
    except:
        pass

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
