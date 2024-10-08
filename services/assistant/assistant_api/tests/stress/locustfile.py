import json

from locust import HttpUser, task

examples = {
    "start": """{"meta":{"locale":"ru-RU","timezone":"UTC","client_id":"ru.yandex.searchplugin/7.16 (none none; android 4.4.2)","interfaces":{"screen":{},"account_linking":{},"audio_player":null}},"request":{"type":"SimpleUtterance","command":"","original_utterance":"","markup":{"dangerous_context":false},"payload":null,"nlu":{"tokens":[],"entities":[],"intents":{}}},"session":{"message_id":0,"session_id":"31e05f3b-020f-48b1-a96e-e2503bb96bc0","skill_id":"e2f2c90c-89f8-48be-ade9-c08b2ef780f2","user_id":"176A432A39EB7EFF0B13E268B2F0315AA6C4F7C5B5B6B082B1E08603F8B58D15","user":{"user_id":"BC90015F6BFFA4B727FACD0755A4903DA907AAE895C9E635FF1FA0B07EB66B3C","access_token":null},"application":{"application_id":"176A432A39EB7EFF0B13E268B2F0315AA6C4F7C5B5B6B082B1E08603F8B58D15"},"new":true},"state":{"session":{},"user":{"last_user_request":"","last_user_response":"Рад снова видеть вас. Задавайте ваши вопросы или скажите 'выход' или 'справка'","dialog_node":"hello"},"application":{}},"version":"1.0"}""",
    "help": """{
    "meta": {
        "locale": "ru-RU",
        "timezone": "UTC",
        "client_id": "ru.yandex.searchplugin/7.16 (none none; android 4.4.2)",
        "interfaces": {
            "screen": {},
            "account_linking": {},
            "audio_player": null
        }
    },
    "request": {
        "type": "SimpleUtterance",
        "command": "помощь",
        "original_utterance": "помощь",
        "markup": {
            "dangerous_context": false
        },
        "payload": null,
        "nlu": {
            "tokens": [
                "помощь"
            ],
            "entities": [],
            "intents": {
                "YANDEX.HELP": {
                    "slots": {}
                }
            }
        }
    },
    "session": {
        "message_id": 0,
        "session_id": "31e05f3b-020f-48b1-a96e-e2503bb96bc0",
        "skill_id": "e2f2c90c-89f8-48be-ade9-c08b2ef780f2",
        "user_id": "176A432A39EB7EFF0B13E268B2F0315AA6C4F7C5B5B6B082B1E08603F8B58D15",
        "user": {
            "user_id": "BC90015F6BFFA4B727FACD0755A4903DA907AAE895C9E635FF1FA0B07EB66B3C",
            "access_token": null
        },
        "application": {
            "application_id": "176A432A39EB7EFF0B13E268B2F0315AA6C4F7C5B5B6B082B1E08603F8B58D15"
        },
        "new": false
    },
    "state": {
        "session": {},
        "user": {
            "last_user_request": "",
            "last_user_response": "Рад снова видеть вас. Задавайте ваши вопросы или скажите 'выход' или 'справка'",
            "dialog_node": "start"
        },
        "application": {}
    },
    "version": "1.0"
}""",
    "person_name_by_action_title": """{"meta":{"locale":"ru-RU","timezone":"UTC","client_id":"ru.yandex.searchplugin/7.16 (none none; android 4.4.2)","interfaces":{"screen":{},"account_linking":{},"audio_player":null}},"request":{"type":"SimpleUtterance","command":"кто снял фильм матрица","original_utterance":"кто снял фильм матрица","markup":{"dangerous_context":false},"payload":null,"nlu":{"tokens":["кто","снял","фильм","матрица"],"entities":[],"intents":{"person_name_by_action_title":{"slots":{"role":{"type":"Action","tokens":{"start":1,"end":2},"value":"director"},"title":{"type":"YANDEX.STRING","tokens":{"start":3,"end":4},"value":"матрица"}}}}}},"session":{"message_id":1,"session_id":"31e05f3b-020f-48b1-a96e-e2503bb96bc0","skill_id":"e2f2c90c-89f8-48be-ade9-c08b2ef780f2","user_id":"176A432A39EB7EFF0B13E268B2F0315AA6C4F7C5B5B6B082B1E08603F8B58D15","user":{"user_id":"BC90015F6BFFA4B727FACD0755A4903DA907AAE895C9E635FF1FA0B07EB66B3C","access_token":null},"application":{"application_id":"176A432A39EB7EFF0B13E268B2F0315AA6C4F7C5B5B6B082B1E08603F8B58D15"},"new":false},"state":{"session":{},"user":{"scenario_place":"person_name","last_user_request":"","last_user_reponse":"Спасибо, что обратились к навыку. Жду ваших вопросов! Для выхода скажите 'выход' или 'помощь'","last_user_response":"С возвращением. Жду ваших вопросов! Для выхода скажите 'выход' или 'помощь'","dialog_node":"hello"},"application":{}},"version":"1.0"}""",
    "bye": """{"meta":{"locale":"ru-RU","timezone":"UTC","client_id":"ru.yandex.searchplugin/7.16 (none none; android 4.4.2)","interfaces":{"screen":{},"account_linking":{},"audio_player":null}},"request":{"type":"SimpleUtterance","command":"выход","original_utterance":"выход","markup":{"dangerous_context":false},"payload":null,"nlu":{"tokens":["выход"],"entities":[],"intents":{"bye":{"slots":{}}}}},"session":{"message_id":2,"session_id":"31e05f3b-020f-48b1-a96e-e2503bb96bc0","skill_id":"e2f2c90c-89f8-48be-ade9-c08b2ef780f2","user_id":"176A432A39EB7EFF0B13E268B2F0315AA6C4F7C5B5B6B082B1E08603F8B58D15","user":{"user_id":"BC90015F6BFFA4B727FACD0755A4903DA907AAE895C9E635FF1FA0B07EB66B3C","access_token":null},"application":{"application_id":"176A432A39EB7EFF0B13E268B2F0315AA6C4F7C5B5B6B082B1E08603F8B58D15"},"new":false},"state":{"session":{},"user":{"scenario_place":"person_name","last_user_request":"кто снял фильм матрица","last_user_reponse":"Спасибо, что обратились к навыку. Жду ваших вопросов! Для выхода скажите 'выход' или 'помощь'","last_user_response":"Lilly Wachowski","dialog_node":"person_name"},"application":{}},"version":"1.0"}""",
}


class StressWebhooks(HttpUser):
    @task
    def stressAliceWebhook(self):
        self.client.post(
            "/webhook/alice", json=json.loads(examples.get("start"))
        )
        self.client.post(
            "/webhook/alice", json=json.loads(examples.get("help"))
        )
        self.client.post(
            "/webhook/alice",
            json=json.loads(examples.get("person_name_by_action_title")),
        )
        self.client.post(
            "/webhook/alice", json=json.loads(examples.get("bye"))
        )
