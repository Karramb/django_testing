import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news, comment_text):
    """Аноним не может оставить комментарий."""
    comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': comment_text}
    client.post(url, data=form_data)
    comments_count_after_request = Comment.objects.count()
    assert comments_count == comments_count_after_request


def test_user_can_create_comment(author, author_client, news, comment_text):
    """Авторизованный юзер может оставить комментарий."""
    comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': comment_text}
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count_after_request = Comment.objects.count()
    assert comments_count + 1 == comments_count_after_request
    comment = Comment.objects.last()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_use_bad_words(author_client, news):
    """В комментариях нельзя использовать запрещенные слова."""
    comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count_after_request = Comment.objects.count()
    assert comments_count == comments_count_after_request


def test_author_can_delete_comment(author_client, comment, news):
    """Авто может удалить комментарий."""
    comments_count = Comment.objects.count()
    response = author_client.delete(reverse('news:delete', args=(comment.id,)))
    news_url = reverse('news:detail', args=(news.id,))
    assertRedirects(response, f'{news_url}#comments')
    comments_count_after_request = Comment.objects.count()
    assert comments_count == comments_count_after_request + 1


def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    """Нельзя удалять комментарии других юзеров."""
    comments_count = Comment.objects.count()
    response = not_author_client.delete(reverse(
        'news:delete', args=(comment.id,)))
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client, comment, news, new_comment_text):
    """Автор может редактировать комментарии."""
    comments_count = Comment.objects.count()
    comment = Comment.objects.last()
    edit_url = reverse('news:edit', args=(comment.id,))
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = f'{news_url}#comments'
    form_data = {'text': new_comment_text}
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment_after_request = Comment.objects.last()
    comments_count_after_request = Comment.objects.count()
    assert comment_after_request.text == new_comment_text
    assert comments_count == comments_count_after_request
    assert comment.news == comment_after_request.news
    assert comment.author == comment_after_request.author
    assert comment.created == comment_after_request.created


def test_user_cant_edit_comment_of_another_user(
        not_author_client, comment, comment_text, new_comment_text):
    """Нельзя редактировать комментарии других юзеров."""
    comments_count = Comment.objects.count()
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data = {'text': new_comment_text}
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_after_request = Comment.objects.last()
    comments_count_after_request = Comment.objects.count()
    assert comments_count == comments_count_after_request
    assert comment_after_request.text == comment_text
    assert comment.news == comment_after_request.news
    assert comment.author == comment_after_request.author
    assert comment.created == comment_after_request.created
