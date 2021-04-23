import vk_api
import random
import json
import requests

api_key = 'bc727dc3777a57c2c2d9b43226afb051b2b4870607293d30eb578e18341ff7a0f682a1852e22c816bb05a'

vk = vk_api.VkApi(token=api_key)
vk._auth_token()


def get_button(label, color, payload=""):
    return {
        "action": {
            "type": "text",
            "payload": json.dumps(payload),
            "label": label
        },
        "color": color
    }


keyboard_start = {
    "one_time": False,
    "buttons": [
        [
            get_button(label="Категории", color="default"),
            get_button(label="Новости по категориям", color="default"),
        ],
        [
            get_button(label="Ключевые слова", color="default"),
            get_button(label="Новости по словам", color="default"),
        ]
    ]
}

keyboard_categories = {
    "one_time": False,
    "buttons": [
        [
            get_button(label="Бизнес", color="default"),
            get_button(label="Развлечения", color="default"),
        ],
        [
            get_button(label="Здоровье", color="default"),
            get_button(label="Наука", color="default"),
        ],
        [
            get_button(label="Спорт", color="default"),
            get_button(label="Технологии", color="default"),
        ],
        [
            get_button(label="Главное", color="default"),
            get_button(label="Назад", color="negative"),
        ]
    ]
}

keyboard_keywords = {
    "one_time": False,
    "buttons":
        [
            [
                get_button(label="Добавить слово", color="default"),
                get_button(label="Удалить слово", color="default")
            ],
            [
                get_button(label="Назад", color="negative")
            ]
        ]
}

keyboard_categories = json.dumps(keyboard_categories, ensure_ascii=False).encode("utf-8")
keyboard_categories = str(keyboard_categories.decode("utf-8"))
keyboard_start = json.dumps(keyboard_start, ensure_ascii=False).encode("utf-8")
keyboard_start = str(keyboard_start.decode("utf-8"))
keyboard_keywords = json.dumps(keyboard_keywords, ensure_ascii=False).encode("utf-8")
keyboard_keywords = str(keyboard_keywords.decode("utf-8"))

words = {
    "бизнес": "business",
    "развлечения": "entertainment",
    "здоровье": "health",
    "наука": "science",
    "спорт": "sports",
    "технологии": "technology",
    "главное": "general"
}
categories = ["business", "entertainment", "health", "science", "sports", "technology", "general"]

while True:
    messages = vk.method("messages.getConversations", {"offset": 0, "count": 20, "filter": "unread"})
    if messages["count"] > 0:
        msg = messages['items'][0]['last_message']['text'].lower()
        conversation_id = messages['items'][0]['last_message']['conversation_message_id']
        user_id = messages['items'][0]['last_message']['from_id']
        first_name = vk.method('users.get', {'user_ids': user_id})[0]['first_name']
        last_name = vk.method('users.get', {'user_ids': user_id})[0]['last_name']
        if msg == "привет":
            vk.method("messages.send",
                      {"peer_id": user_id, "message": f"{first_name}, Вы зарегистрированы",
                       'random_id': random.randint(1, 231456735)})
            requests.post("http://127.0.0.1:5000/create_user",
                          {"user_id": user_id, "fname": first_name, "lname": last_name})
        elif msg == "категории":
            vk.method("messages.send",
                      {"peer_id": user_id, "message": "Выберите понравишуюся категорию",
                       'random_id': random.randint(1, 231456735), "keyboard": keyboard_categories})
        elif msg in words:
            req = requests.post("http://127.0.0.1:5000/subs_categ",
                                {"user_id": user_id, "category": words[msg], "rus_category": msg}).json()
            vk.method("messages.send",
                      {"peer_id": user_id, "message": req["answer"], 'random_id': random.randint(1, 231456735)})
        elif msg == "ключевые слова":
            req = requests.get(f"http://127.0.0.1:5000/get_keywords/{user_id}").json()
            if len(req["keywords"][0]) < 3:
                vk.method("messages.send",
                          {"peer_id": user_id, "message": "У вас пока нет ключевых слов",
                           'random_id': random.randint(1, 231456735), "keyboard": keyboard_keywords})
            else:
                string = "Ваши ключевые слова:\n"
                for key in req["keywords"]:
                    string = string + key + "\n"
                vk.method("messages.send",
                          {"peer_id": user_id, "message": string,
                           'random_id': random.randint(1, 231456735), "keyboard": keyboard_keywords})
            vk.method("messages.send",
                      {"peer_id": user_id, "message": "Нажмите добавить или удалить и введите ключевое слово",
                       'random_id': random.randint(1, 231456735), "keyboard": keyboard_keywords})
        elif msg == "добавить слово":
            vk.method("messages.send",
                      {"peer_id": user_id, "message": "Введите слово которое хотите добавить",
                       'random_id': random.randint(1, 231456735)})
        elif msg == "удалить слово":
            vk.method("messages.send",
                      {"peer_id": user_id, "message": "Введите слово которое хотите удалить",
                       'random_id': random.randint(1, 231456735)})
        elif msg == "назад":
            vk.method("messages.send",
                      {"peer_id": user_id, "message": "Вы попали в главное меню",
                       'random_id': random.randint(1, 231456735), "keyboard": keyboard_start})
        elif msg == "новости по категориям":
            req = requests.get(f"http://127.0.0.1:5000/get_news/{user_id}").json()
            if req == {}:
                vk.method("messages.send", {"peer_id": user_id,
                                            "message": "У вас нет подписок на категории",
                                            'random_id': random.randint(0, 231456735), "keyboard": keyboard_start})
            for title in req:
                vk.method("messages.send", {"peer_id": user_id,
                                            "message": title,
                                            'random_id': random.randint(0, 231456735), "keyboard": keyboard_start})
                if req[title]["count"] == 0:
                    vk.method("messages.send", {"peer_id": user_id,
                                                "message": "Новостей в этой категории в данный момент нет",
                                                'random_id': random.randint(0, 231456735), "keyboard": keyboard_start})
                for i in range(0, req[title]["count"]):
                    vk.method("messages.send", {"peer_id": user_id,
                                                "message": str(req[title]["titles"][i] + "\n" + req[title]["urls"][i]),
                                                'random_id': random.randint(0, 231456735), "keyboard": keyboard_start})
        elif msg == "новости по словам":
            req = requests.get(f"http://127.0.0.1:5000/get_keynews/{user_id}").json()
            if req == {} or req[""]:
                vk.method("messages.send", {"peer_id": user_id,
                                            "message": "У вас нет ключевых слов",
                                            'random_id': random.randint(0, 231456735), "keyboard": keyboard_start})
            for title in req:
                if title == "":
                    continue
                vk.method("messages.send", {"peer_id": user_id,
                                            "message": title,
                                            'random_id': random.randint(0, 231456735), "keyboard": keyboard_start})
                if req[title]["count"] == 0:
                    vk.method("messages.send", {"peer_id": user_id,
                                                "message": "Новостей по этому ключевому слову не найдено",
                                                'random_id': random.randint(0, 231456735), "keyboard": keyboard_start})
                for i in range(0, req[title]["count"]):
                    vk.method("messages.send", {"peer_id": user_id,
                                                "message": str(req[title]["titles"][i] + "\n" + req[title]["urls"][i]),
                                                'random_id': random.randint(0, 231456735), "keyboard": keyboard_start})
        elif msg != "":
            req = requests.post("http://127.0.0.1:5000/subs_keywords", {"user_id": user_id, "keywords": msg}).json()
            if req["status"] == "del":
                vk.method("messages.send",
                          {"peer_id": user_id, "message": "Слово было удалено",
                           'random_id': random.randint(1, 231456735), "keyboard": keyboard_keywords})
            elif req["status"] == "add":
                vk.method("messages.send",
                          {"peer_id": user_id, "message": "Слово было добавлено",
                           'random_id': random.randint(1, 231456735), "keyboard": keyboard_keywords})
