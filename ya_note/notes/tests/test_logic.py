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
        cls.NOTES_SUCCESS = reverse('notes:success')
        cls.USER_LOGIN = reverse('users:login')
        cls.NOTES_ADD = reverse('notes:add')
        cls.REDIRECT_FROM_ADD = f'{cls.USER_LOGIN}?next={cls.NOTES_ADD}'

    def test_user_can_create_note(self):
        """Авторизованный юзер может создать заметку."""
        self.note.delete()
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)
        response = self.auth_client.post(self.NOTES_ADD, data=self.form_data)
        note_for_test = Note.objects.last()
        self.assertEqual(note_count + 1, Note.objects.count())
        self.assertRedirects(response, self.NOTES_SUCCESS)
        self.assertEqual(note_for_test.title, self.form_data['title'])
        self.assertEqual(note_for_test.text, self.form_data['text'])
        self.assertEqual(note_for_test.slug, self.form_data['slug'])
        self.assertEqual(note_for_test.author, self.author)

    def test_anonim_cant_create_note(self):
        """Заметку может создать только зарегистрированный юзер."""
        note_count = Note.objects.count()
        response = self.client.post(self.NOTES_ADD, data=self.form_data)
        self.assertRedirects(response, self.REDIRECT_FROM_ADD)
        self.assertEqual(Note.objects.count(), note_count)

    def test_not_unique_slug(self):
        """Слаг может быть только уникальным."""
        note_count = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        self.auth_client.post(reverse('notes:add'), data=self.form_data)
        self.assertEqual(Note.objects.count(), note_count)

    def test_empty_slug(self):
        """С пустым слагом можно создать заметку."""
        self.note.delete()
        self.assertEqual(Note.objects.count(), 0)
        self.form_data.pop('slug')
        self.auth_client.post(reverse('notes:add'), data=self.form_data)
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.last()
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_note(self):
        """Автор может редактировать заметку."""
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        response = self.auth_client.post(self.EDIT_NOTE, self.form_data)
        self.assertEqual(note_count, 1)
        note_after_request = Note.objects.last()
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(note_after_request.title, self.form_data['title'])
        self.assertEqual(note_after_request.slug, self.form_data['slug'])
        self.assertEqual(note_after_request.text, self.form_data['text'])
        self.assertEqual(note_after_request.author, self.note.author)

    def test_author_can_delete_note(self):
        """Автор может удалить заметку."""
        note_count = Note.objects.count()
        response = self.auth_client.post(self.DELETE_NOTE)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), note_count - 1)

    def test_other_user_cant_delete_note(self):
        """Не авто не может удалить заметку."""
        note_count = Note.objects.count()
        self.client.post(self.DELETE_NOTE)
        self.assertEqual(Note.objects.count(), note_count)

    def test_other_user_cant_edit_note(self):
        """Не автор не может редактировать заметку."""
        self.client.post(self.EDIT_NOTE, self.form_data)
        note_after_request = Note.objects.last()
        self.assertNotEqual(note_after_request.title, self.form_data['title'])
