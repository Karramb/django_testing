import pytest

from datetime import datetime, timedelta
from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client

@pytest.fixture
@pytest.mark.django_db
def news():
    news = News.objects.create(title='Заголовок', text='Текст')
    return news

@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment

@pytest.fixture
@pytest.mark.django_db
def news_11():
    all_news = []
    today = datetime.today()
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News.objects.create(
            title='Заголовок',
            text='Текст',
            date=today - timedelta(days=index)
        )
        all_news.append(news)
    return all_news

@pytest.fixture
@pytest.mark.django_db
def comments(author, news):
    all_comments = []
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text='text_comment'
        )
        comment.created = now + timedelta(days=index)
        all_comments.append(comment)
    return all_comments
