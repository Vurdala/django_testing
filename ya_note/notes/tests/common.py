from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class BaseSetUp(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Test_author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Test_not_author')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Заглавие',
            text='Текст',
            slug='test_note',
            author=cls.author
        )
