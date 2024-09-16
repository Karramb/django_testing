from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')
BASE_CLIENT = pytest.lazy_fixture('client')
HOME_URL = pytest.lazy_fixture('home_url')
USER_LOGIN = pytest.lazy_fixture('users_login')
USER_LOGOUT = pytest.lazy_fixture('users_logout')
USER_SIGNUP = pytest.lazy_fixture('users_signup')
DETAIL_URL = pytest.lazy_fixture('detail_url')
NEWS_EDIT = pytest.lazy_fixture('news_edit')
NEWS_DELETE = pytest.lazy_fixture('news_delete')


@pytest.mark.parametrize(
    'name, client_type, expected_status',
    (
        (HOME_URL, NOT_AUTHOR_CLIENT, HTTPStatus.OK),
        (USER_LOGIN, NOT_AUTHOR_CLIENT, HTTPStatus.OK),
        (USER_LOGOUT, NOT_AUTHOR_CLIENT, HTTPStatus.OK),
        (USER_SIGNUP, NOT_AUTHOR_CLIENT, HTTPStatus.OK),
        (DETAIL_URL, BASE_CLIENT, HTTPStatus.OK),
        (NEWS_EDIT, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (NEWS_DELETE, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (NEWS_EDIT, AUTHOR_CLIENT, HTTPStatus.OK),
        (NEWS_DELETE, AUTHOR_CLIENT, HTTPStatus.OK),
    )
)
def test_pages_availability(client_type, expected_status, name):
    """Проверка доступности страниц (не)авторизованному юзеру."""
    response = client_type.get(name)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (NEWS_EDIT, NEWS_DELETE)
)
def test_redirect_for_anonymous_client(client, users_login, name, comment):
    """Проверка переадресации неавторизованного юзера."""
    redirect_url = f'{users_login}?next={name}'
    response = client.get(name)
    assertRedirects(response, redirect_url)
