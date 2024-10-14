from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING
from pytils.translit import slugify
from notes.tests.common import BaseSetUp

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


class TestNoteCreation(BaseSetUp):

    @classmethod
    def setUpTestData(cls):
        super(TestNoteCreation, cls).setUpTestData()
        cls.url = reverse('notes:add')
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
        count_notes = Note.objects.count()
        response = self.author_client.post(self.url, data=self.notes_info)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), count_notes + 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.notes_info['title'])
        self.assertEqual(new_note.text, self.notes_info['text'])
        self.assertEqual(new_note.slug, self.notes_info['slug'])
        self.assertEqual(new_note.author, self.user)

    def test_anonymous_user_cant_create_note(self):
        count_notes = Note.objects.count()
        response = self.client.post(self.url, data=self.notes_info)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), count_notes)

    def test_not_unique_slug(self):
        self.new_notes_info['slug'] = self.note.slug
        count_notes = Note.objects.count()
        response = self.author_client.post(self.url, data=self.new_notes_info)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), count_notes)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.new_notes_info.pop('slug')
        response = self.author_client.post(url, data=self.new_notes_info)
        self.assertRedirects(response, reverse('notes:success'))
        new_note = Note.objects.get(title='Заголовок')
        expected_slug = slugify(self.new_notes_info['title'])
        self.assertEqual(new_note.slug, expected_slug)


class ChangeNote(BaseSetUp):

    @classmethod
    def setUpTestData(cls):
        super(ChangeNote, cls).setUpTestData()
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = NEW_NOTES_INFO

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.form_data['title'])
        self.assertEqual(note_from_db.text, self.form_data['text'])
        self.assertEqual(note_from_db.slug, self.form_data['slug'])
        self.assertEqual(note_from_db.author, self.author)

    def test_author_can_delete_note(self):
        count_notes = Note.objects.count()
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), count_notes - 1)

    def test_other_user_cant_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        count_notes = Note.objects.count()
        response = self.not_author_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), count_notes)

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.not_author_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
