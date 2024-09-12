from django.test import TestCase
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
        self.client.force_login(self.author)
        for name in (self.CREATE_URL, self.EDIT_NOTE):
            response = self.client.get(name)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_in_list_context(self):
        self.client.force_login(self.author)
        response = self.client.get(self.NOTE_LIST)
        self.assertIn(self.note, response.context['object_list'])

    def test_not_in_the_left_list(self):
        self.client.force_login(self.reader)
        response = self.client.get(self.NOTE_LIST)
        self.assertNotIn(self.note, response.context['object_list'])
