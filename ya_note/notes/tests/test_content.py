from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Чел Простой')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Тест',
            text='Тест',
            slug='note_test',
            author=cls.author
        )
        cls.CREATE_URL = reverse('notes:add')
        cls.EDIT_NOTE = reverse('notes:edit', args=(cls.note.slug,))
        cls.NOTE_LIST = reverse('notes:list')

    def test_authorized_client_has_form(self):
        """Форма создания заметки есть у авторизованного юзера."""
        urls = (self.CREATE_URL, self.EDIT_NOTE)
        for url in urls:
            with self.subTest():
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_in_list_context(self):
        """Заметка есть в контексте на странице списка заметок."""
        response = self.auth_client.get(self.NOTE_LIST)
        object_list = response.context['object_list']
        note_for_test = object_list[0]
        self.assertEqual(object_list.count(), 1)
        self.assertEqual(note_for_test.title, self.note.title)
        self.assertEqual(note_for_test.text, self.note.text)
        self.assertEqual(note_for_test.slug, self.note.slug)
        self.assertEqual(note_for_test.author, self.note.author)

    def test_note_in_the_left_list(self):
        """Чужие заметки не попадают на страницу пользователя."""
        response = self.reader_client.get(self.NOTE_LIST)
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 0)
