from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING
from pytils.translit import slugify


User = get_user_model()


NOTES_INFO = {
    'title': 'Заглавие',
    'text': 'Текст',
    'slug': 'test_note',
}
NEW_NOTES_INFO = {
    'title': 'Заголовок',
    'text': 'Текст',
    'slug': 'new-slug',
}


class TestNoteCreation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='test_user')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        cls.notes_info = {
            'title': 'Заглавие',
            'text': 'Текст',
            'slug': 'test_note',
        }
        cls.new_notes_info = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'new-slug',
        }

    def test_auth_user_can_create_notes(self):
        response = self.auth_client.post(self.url, data=self.notes_info)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.notes_info['title'])
        self.assertEqual(new_note.text, self.notes_info['text'])
        self.assertEqual(new_note.slug, self.notes_info['slug'])
        self.assertEqual(new_note.author, self.user)

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.url, data=self.notes_info)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test_note',
            author=self.user
        )
        self.new_notes_info['slug'] = note.slug
        response = self.auth_client.post(self.url, data=self.new_notes_info)
        self.assertFormError(
            response, 'form', 'slug', errors=(note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.new_notes_info.pop('slug')
        response = self.auth_client.post(url, data=self.new_notes_info)
        self.assertRedirects(response, reverse('notes:success'))
        new_note = Note.objects.get()
        expected_slug = slugify(self.new_notes_info['title'])
        self.assertEqual(new_note.slug, expected_slug)


class ChangeNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test_note',
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = NEW_NOTES_INFO

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.author)

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.reader_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.reader_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
