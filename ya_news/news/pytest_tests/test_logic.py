import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError
from http import HTTPStatus

from news.models import News, Comment
from news.forms import BAD_WORDS, WARNING


def test_user_can_create_comment(author_client, author, news, form_data_old):
    COMMENT_TEXT = 'Текст комментария'
    url = reverse('news:detail', args=(news.id,))

    response = author_client.post(url, data=form_data_old)

    assertRedirects(response, f'{url}#comments')

    comments_count = Comment.objects.count()

    assert comments_count == 1

    comment = Comment.objects.get()

    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, form_data_old, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data_old)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert News.objects.count() == 1


def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, news, comment):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.delete(reverse('news:delete', args=(comment.id,)))
    assertRedirects(response, url + '#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
    news, not_author_client, comment
):
    response = not_author_client.delete(
        reverse('news:delete', args=(comment.id,))
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


def test_author_can_edit_comment(author_client, news, comment, form_data_new):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(
        reverse('news:edit', args=(comment.id,)), data=form_data_new)
    assertRedirects(response, url + '#comments')
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
    not_author_client, news, comment, form_data_old
):
    response = not_author_client.post(
        reverse('news:edit', args=(comment.id,)), data=form_data_old
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
