from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.forms import NoteForm
from notes.tests.common import BaseSetUp
from notes.models import Note

User = get_user_model()


class TestContent(BaseSetUp):
    @classmethod
    def setUpTestData(cls):
        super(TestContent, cls).setUpTestData()
        all_news = [
            Note(
                title=f'Новость {index}',
                text='Просто текст.',
                slug=f'slug_{index}',
                author=cls.author
            )
            for index in range(10)
        ]
        Note.objects.bulk_create(all_news)

    def test_note_in_list_for_users(self):
        url = reverse('notes:list')
        author_results = (
            (self.author_client, True),
            (self.not_author_client, False),
        )
        for user, result in author_results:
            with self.subTest(user=user, result=result):
                response = user.get(url)
                object_list = response.context['object_list']
                self.assertEqual(
                    (self.assertIn(self.note, object_list)), result
                )

    def test_authorized_client_has_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls:
            with self.subTest(name=name):
                self.client.force_login(self.author)
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
