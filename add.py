import sqlite3 as sq
import random
import requests
import json

connect = sq.connect("db.sqlite", check_same_thread=False)
cursor = connect.cursor()


def create_database():
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        "id"	INTEGER NOT NULL UNIQUE,
        "fname"	TEXT,
        "lname"	TEXT,
        PRIMARY KEY("id")
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
        "id"	INTEGER NOT NULL UNIQUE,
        "business"	INTEGER NOT NULL DEFAULT 0,
        "entertainment"	INTEGER NOT NULL DEFAULT 0,
        "health"	INTEGER NOT NULL DEFAULT 0,
        "science"	INTEGER NOT NULL DEFAULT 0,
        "sports"	INTEGER NOT NULL DEFAULT 0,
        "technology"	INTEGER NOT NULL DEFAULT 0,
        "general"	INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY("id")
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS keywords (
        "id"	INTEGER NOT NULL UNIQUE,
        "keywords"	TEXT,
        PRIMARY KEY("id")
    )''')
    connect.commit()


def reg_user(id, fname, lname):
    req_users = """INSERT INTO users ("id","fname","lname") VALUES (?,?,?)"""
    req_cats = '''INSERT INTO categories ("id") VALUES (?)'''
    req_keys = '''INSERT INTO keywords ("id") VALUES (?)'''
    cursor.execute(req_users, (id, fname, lname,))
    cursor.execute(req_cats, (id,))
    cursor.execute(req_keys, (id,))
    connect.commit()


def user_exist(id):
    request = '''SELECT * FROM users WHERE id LIKE (?)'''
    answer = cursor.execute(request, (id,))
    answer = answer.fetchone()
    return answer


def select_req(id):
    one_result = cursor.execute('''SELECT * FROM categories WHERE id LIKE (?)''', (id,))
    one_result = one_result.fetchone()
    return one_result


rus_categories = ["Бизнес", "Развлечения", "Здоровье", "Наука", "Спорт", "Технологии", "Главное"]
categories = ["business", "entertainment", "health", "science", "sports", "technology", "general"]


def get_news(id):
    ex_cat = select_req(id)
    result = {}
    for i in range(1, 8):
        if ex_cat[i] == 1:
            link = f"https://newsapi.org/v2/top-headlines?apiKey=2df071e0ab3c417d9626cef194e3d41a&country=ru&category={categories[i - 1]}&pageSize=3"
            link = requests.get(link)
            link = link.json()
            total_result = link['totalResults']
            if total_result > 3:
                total_result = 3
            title = rus_categories[i - 1].capitalize()
            titles = []
            urls = []
            for n in range(0, total_result):
                titles.append(str(link['articles'][n]['title']))
                urls.append(str(link['articles'][n]['url']))
            result.update({
                title: {
                    "titles": titles,
                    "urls": urls,
                    "count": total_result
                }
            })
    return result


def edit_categ(id, category, category_rus):
    sel_cat = cursor.execute('''SELECT {} FROM categories WHERE id LIKE {}'''.format(category, id, ))
    sel_cat = sel_cat.fetchone()
    if sel_cat[0] == 1:
        cursor.execute('''UPDATE categories SET {}=0 WHERE id LIKE {}'''.format(category, id, ))
        connect.commit()
        return "Вы отписались от категории " + category_rus
    else:
        cursor.execute('''UPDATE categories SET {}=1 WHERE id LIKE {}'''.format(category, id, ))
        connect.commit()
        return "Вы подписались на категорию " + category_rus


def add_keywords(id, keywords):
    sel_kw = cursor.execute('''SELECT keywords FROM keywords WHERE id LIKE {}'''.format(id, ))
    sel_kw = sel_kw.fetchone()
    sel_kw = list(sel_kw)
    sel_kw.append(keywords)
    try:
        sel_kw.remove(None)
    except ValueError:
        pass
    sel_kw = str(sel_kw).replace("[", "")
    sel_kw = sel_kw.replace("]", "")
    sel_kw = sel_kw.replace("'", "")
    sel_kw = sel_kw.replace('"', '')
    sel_kw = sel_kw.replace('\\', '')
    cursor.execute('''UPDATE keywords SET keywords=? WHERE id LIKE ?''', (sel_kw, id,))
    connect.commit()


def get_keynews(id):
    keywords = select_keywords(id)
    result = {}
    for i in keywords:
        link = f"https://newsapi.org/v2/top-headlines?apiKey=2df071e0ab3c417d9626cef194e3d41a&country=ru&q={i}&pageSize=3"
        link = requests.get(link)
        link = link.json()
        total_result = link['totalResults']
        if total_result > 3:
            total_result = 3
        title = i.capitalize()
        titles = []
        urls = []
        for n in range(0, total_result):
            titles.append(str(link['articles'][n]['title']))
            urls.append(str(link['articles'][n]['url']))
        result.update({
            title: {
                "titles": titles,
                "urls": urls,
                "count": total_result
            }
        })
    return result




def select_keywords(id):
    sel_kw = cursor.execute('''SELECT keywords FROM keywords WHERE id LIKE {}'''.format(id, ))
    sel_kw = sel_kw.fetchone()
    sel_kw = list(sel_kw)
    sel_kw = str(sel_kw).replace("[", "")
    sel_kw = sel_kw.replace("]", "")
    sel_kw = sel_kw.replace("'", "")
    sel_kw = sel_kw.replace('"', '')
    sel_kw = sel_kw.replace('\\', '')
    string = str(sel_kw)
    string = string.replace(" ", "").split(",")
    string = list(string)
    return string


def del_keywords(id, word):
    key_words = select_keywords(id)
    index = key_words.index(word)
    key_words = str(key_words).replace("[", "")
    key_words = key_words.replace("]", "")
    key_words = key_words.replace("'", "")
    key_words = key_words.replace('"', '')
    key_words = key_words.replace('\\', '')
    key_words = key_words.split(",")
    key_words.pop(index)
    cursor.execute('''UPDATE keywords SET keywords=? WHERE id LIKE ?''', (str(key_words), id,))
    connect.commit()


def del_or_add_keyword(id, word):
    keywords = select_keywords(id)
    if word in keywords:
        del_keywords(id, word)
        return "del"
    else:
        add_keywords(id, word)
        return "add"
