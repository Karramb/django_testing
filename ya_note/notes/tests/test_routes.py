from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Тест', text='Тест', slug='note_test', author=cls.author)
        notes_home = reverse('notes:home', None)
        users_login = reverse('users:login', None)
        users_logout = reverse('users:logout', None)
        users_signup = reverse('users:signup', None)
        notes_list = reverse('notes:list', None)
        notes_success = reverse('notes:success', None)
        notes_add = reverse('notes:add', None)
        cls.notes_detail = reverse('notes:detail', args=(cls.note.slug,))
        cls.notes_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.notes_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.urls_for_all = (
            notes_home,
            users_login,
            users_logout,
            users_signup,
        )
        cls.urls_for_authorized_user = (
            notes_list,
            notes_success,
            notes_add,
            cls.notes_detail,
            cls.notes_edit,
            cls.notes_delete,
        )
        cls.all_urls = cls.urls_for_authorized_user + cls.urls_for_all
        cls.LOGIN_URL = reverse('users:login')

    def test_for_author(self):
        """Автор может зайти на все страницы."""
        for url in self.all_urls:
            with self.subTest(user=self.author, url=url):
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_for_reader(self):
        """Обычный юзер может зайти на все страницы кроме чужих заметок."""
        for url in self.urls_for_authorized_user:
            with self.subTest(user=self.reader):
                response = self.reader_client.get(url)
                if url in (
                    self.notes_detail,
                    self.notes_edit,
                    self.notes_delete
                ):
                    self.assertEqual(
                        response.status_code,
                        HTTPStatus.NOT_FOUND
                    )
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_for_anonim_user(self):
        """Анониму доступны только страницы логина/регистрации и главная."""
        for url in self.all_urls:
            with self.subTest():
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                if (url) in self.urls_for_authorized_user:
                    self.assertRedirects(response, redirect_url)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
