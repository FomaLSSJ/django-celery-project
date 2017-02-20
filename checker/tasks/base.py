from __future__ import absolute_import
from celery import shared_task, group
from ..celery import app
from lxml import html
from django.core.mail import EmailMessage

from checker.models import Game

import requests, json

url_home = 'https://refuge.tokyo/pc9801'


@app.task
def test(param):
    return 'The test task executed with argument "%s"' % (param)


@app.task
def result(value):
    return 'Result: %s' % (value)


@app.task
def sum(x, y):
    return x + y


@app.task
def get(desc=None, date=None):
    url = 'https://www.renpy.org/release_list.html'
    
    session = requests.Session()
    page = session.get(url)
    tree = html.fromstring(page.content)
    
    version = tree.cssselect('table.table tr.off td')[1].text_content().strip()
    description = tree.cssselect('table.table tr.off td')[2].text_content().strip()
    release = tree.cssselect('table.table tr.off td')[3].text_content().strip()
    
    res = [version]
    
    if desc:
        res.append(description)
    if date:
        res.append(release)

    return ' - '.join(res)


@app.task
def send():
    email = EmailMessage(
        'Django Sender', 
        'Adam Sender (Azaza, very funny joke!)', 
        to=['monsterfoma@gmail.com']
    )

    return bool(email.send())


@app.task
def get_main_page():
    url = '%s/pc9801.html' % (url_home)

    session = requests.Session()
    page = session.get(url, verify=False)
    tree = html.fromstring(page.content)

    menu = tree.cssselect('div#genre-navi a')
    menu.pop()
    menu.pop()

    return group(get_category_page.s(e.get('href')) for e in menu).apply_async()


@app.task
def get_category_page(href):
    url = '%s/%s' % (url_home, href)

    session = requests.Session()
    page = session.get(url, verify=False)
    tree = html.fromstring(page.content)

    menu = tree.cssselect('div#sub-genre a')

    return group(get_games_list.s(e.get('href')) for e in menu).apply_async()


@app.task
def get_games_list(href):
    url = '%s/%s' % (url_home, 'Adventure_Aa.html')

    session = requests.Session()
    page = session.get(url, verify=False)
    tree = html.fromstring(page.content)

    games = tree.cssselect('div#gamelist a')

    return group(get_game_info.s(i.get('href')) for i in games).apply_async()


@app.task
def get_game_info(href):
    url = '%s/%s' % (url_home, href)
    
    session = requests.Session()
    page = session.get(url, verify=False)
    tree = html.fromstring(page.content)
    
    article_id = href.split('/')[1].split('.')[0]
    title_jp = tree.cssselect('div#title_jp')[0].text_content().strip()
    title_en = tree.cssselect('div#title_en')[0].text_content().strip()
    data = (tree.cssselect('div#publisher')[0].text_content().strip()).split('|')
    publisher = data[0].split(':')[1].strip()
    release = data[1].split(':')[1]
    media = data[2].split(':')[1].strip()

    Game.objects.create(
        article_id=int(article_id),
        title_jp=title_jp.strip(),
        title_en=title_en.strip(),
        publisher=publisher if len(publisher) else None,
        release=len(release) if len(release) else None,
        media=media if len(media) else None
    )

    print('Add game id: %s' % (article_id))
    return article_id
