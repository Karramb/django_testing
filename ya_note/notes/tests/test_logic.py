from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note


User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Чел Простой')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Тест',
            'text': 'Тест',
            'slug': 'note_test'
        }
        cls.note = Note.objects.create(
            title='Тест1',
            text='Тест1',
            slug='note_test1',
            author=cls.author
        )
        cls.CREATE_URL = reverse('notes:add')
        cls.EDIT_NOTE = reverse('notes:edit', args=(cls.note.slug,))
        cls.NOTE_LIST = reverse('notes:list')
        cls.DELETE_NOTE = reverse('notes:delete', args=(cls.note.slug,))

    def test_user_can_create_note(self):
        client_list = (
            (self.auth_client, '/done/'),
            (self.client, '/auth/login/?next=/add/')
        )
        for client, name in client_list:
            response = client.post(reverse('notes:add'), data=self.form_data)
            self.assertRedirects(response, name)

    def test_not_unique_slug(self):
        self.form_data['slug'] = self.note.slug
        self.auth_client.post(reverse('notes:add'), data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        self.auth_client.post(reverse('notes:add'), data=self.form_data)
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(Note.objects.count(), 2)
        self.assertEqual(Note.objects.last().slug, expected_slug)

    def test_author_can_edit_note(self):
        response = self.auth_client.post(self.EDIT_NOTE, self.form_data)
        self.note.refresh_from_db()
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(self.note.title, self.form_data['title'])

    def test_author_can_delete_note(self):
        response = self.auth_client.post(self.DELETE_NOTE)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        self.client.post(self.DELETE_NOTE)
        self.assertEqual(Note.objects.count(), 1)

    def test_other_user_cant_edit_note(self):
        self.client.post(self.EDIT_NOTE, self.form_data)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, self.form_data['title'])
