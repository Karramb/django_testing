import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.utils import timezone
from django.urls import reverse

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
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News.objects.create(
            title='Заголовок',
            text='Текст',
        )


@pytest.fixture
@pytest.mark.django_db
def comments(author, news):
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text='text_comment'
        )

@pytest.fixture
def comment_text():
    return 'Текст комментария'

@pytest.fixture
def new_comment_text():
    return 'Обновлённый комментарий'

@pytest.fixture
def home_url():
    return reverse('news:home', None)

@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))

@pytest.fixture
def news_delete(comment):
    return reverse('news:delete', args=(comment.id,))

@pytest.fixture
def news_edit(comment):
    return reverse('news:edit', args=(comment.id,))

@pytest.fixture
def users_login():
    return reverse('users:login', None)

@pytest.fixture
def users_logout():
    return reverse('users:logout', None)

@pytest.fixture
def users_signup():
    return reverse('users:signup', None)
