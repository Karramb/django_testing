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
        notes_home = reverse('notes:home')
        cls.users_login = reverse('users:login')
        users_logout = reverse('users:logout')
        users_signup = reverse('users:signup')
        cls.notes_list = reverse('notes:list')
        cls.notes_success = reverse('notes:success')
        cls.notes_add = reverse('notes:add')
        cls.notes_detail = reverse('notes:detail', args=(cls.note.slug,))
        cls.notes_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.notes_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.all_urls = (
            cls.notes_list,
            cls.notes_success,
            cls.notes_add,
            cls.notes_detail,
            cls.notes_edit,
            cls.notes_delete,
            notes_home,
            cls.users_login,
            users_logout,
            users_signup,
        )

    def test_for_author(self):
        """Автор может зайти на все страницы."""
        for url in self.all_urls:
            with self.subTest(user=self.author, url=url):
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_for_reader(self):
        """Обычный юзер может зайти на все страницы кроме чужих заметок."""
        urls_when_wait_404 = (
            self.notes_detail,
            self.notes_edit,
            self.notes_delete
        )
        for url in self.all_urls:
            with self.subTest(user=self.reader, url=url):
                response = self.reader_client.get(url)
                if url in urls_when_wait_404:
                    self.assertEqual(
                        response.status_code,
                        HTTPStatus.NOT_FOUND
                    )
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_for_anonim_user(self):
        """Анониму доступны только страницы логина/регистрации и главная."""
        urls_for_authorized_user = (
            self.notes_list,
            self.notes_success,
            self.notes_add,
            self.notes_detail,
            self.notes_edit,
            self.notes_delete,
        )
        for url in self.all_urls:
            with self.subTest(url=url):
                redirect_url = f'{self.users_login}?next={url}'
                response = self.client.get(url)
                if url in urls_for_authorized_user:
                    self.assertRedirects(response, redirect_url)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
