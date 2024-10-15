from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.forms import NoteForm
from notes.tests.common import BaseSetUp


User = get_user_model()


class TestContent(BaseSetUp):
    @classmethod
    def setUpTestData(cls):
        super(TestContent, cls).setUpTestData()
    
    #Я пытался объединить, но у меня вообще никак не получалось(((
    def test_note_in_list_for_author(self):
        url = reverse('notes:list')
        response = self.author_client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        url = reverse('notes:list')
        response = self.not_author_client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

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
