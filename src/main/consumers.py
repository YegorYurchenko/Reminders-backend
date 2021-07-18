""" Main consumer """

import json
from channels.generic.websocket import WebsocketConsumer

class ReminderConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data: dict):
        text_data_json = json.loads(text_data)
        type = text_data_json['type']

        if type == 'initialization':
            data = get_initialization_data()

        if type == 'removeRemind':
            data = {
                "type": "removeRemind",
                "status": "success"
            }

        if type == 'newRemind': # ДОДЕЛАТЬ (возвращаем id для нового Remind)
            data = {
                "type": "newRemind",
                "status": "success",
                "data": {
                    "id": "433"
                }
            }

        if type == 'editRemind':
            data = {
                "type": "editRemind",
                "status": "success"
            }

        self.send(text_data=json.dumps({
            'data': data
        }))

def get_initialization_data() -> dict:
    data = {
        "type": "initialization",
        "status": "success",
        "data": [
            {
                "id": "remind_1",
                "title": "Meet with Joe",
                "date": {
                    "year": "2024",
                    "month": "07",
                    "day": "28"
                },
                "time": {
                    "hour": "12",
                    "minute": "00"
                }
            },
            {
                "id": "remind_2",
                "title": "Buy grosserys",
                "date": {
                    "year": "2024",
                    "month": "09",
                    "day": "05"
                },
                "time": {
                    "hour": "15",
                    "minute": "25"
                }
            },
            {
                "id": "remind_3",
                "title": "Take swimming lesson",
                "date": {
                    "year": "2025",
                    "month": "11",
                    "day": "23"
                },
                "time": {
                    "hour": "09",
                    "minute": "15"
                }
            },
            {
                "id": "remind_4",
                "title": "Visit mom",
                "date": {
                    "year": "2026",
                    "month": "02",
                    "day": "15"
                },
                "time": {
                    "hour": "21",
                    "minute": "40"
                }
            }
        ]
    }

    return data
