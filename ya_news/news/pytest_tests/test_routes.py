import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db
@pytest.mark.parametrize(
    'name, client_type, expected_status',
    (
        (pytest.lazy_fixture('home_url'),
         pytest.lazy_fixture('not_author_client'),
         HTTPStatus.OK
         ),
        (pytest.lazy_fixture('users_login'),
         pytest.lazy_fixture('not_author_client'),
         HTTPStatus.OK
         ),
        (pytest.lazy_fixture('users_logout'),
         pytest.lazy_fixture('not_author_client'),
         HTTPStatus.OK
         ),
        (pytest.lazy_fixture('users_signup'),
         pytest.lazy_fixture('not_author_client'),
         HTTPStatus.OK
         ),
        (pytest.lazy_fixture('detail_url'),
         pytest.lazy_fixture('client'),
         HTTPStatus.OK
         ),
        (pytest.lazy_fixture('news_edit'),
         pytest.lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND
         ),
        (pytest.lazy_fixture('news_delete'),
         pytest.lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND
         ),
        (pytest.lazy_fixture('news_edit'),
         pytest.lazy_fixture('author_client'),
         HTTPStatus.OK
         ),
        (pytest.lazy_fixture('news_delete'),
         pytest.lazy_fixture('author_client'),
         HTTPStatus.OK
         ),
    )
)
def test_pages_availability(client_type, expected_status, name):
    """Проверка доступности страниц (не)авторизованному юзеру."""
    response = client_type.get(name)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (pytest.lazy_fixture('news_edit'), pytest.lazy_fixture('news_delete'))
)
def test_redirect_for_anonymous_client(client, users_login, name, comment):
    """Проверка переадресации неавторизованного юзера."""
    redirect_url = f'{users_login}?next={name}'
    response = client.get(name)
    assertRedirects(response, redirect_url)
