import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError
from http import HTTPStatus

from news.models import News, Comment
from news.forms import BAD_WORDS, WARNING


def test_user_can_create_comment(author_client, author, news, form_data_old):
    COMMENT_TEXT = 'Текст комментария'
    url = reverse('news:detail', args=(news.id,))
    count_comments_before = Comment.objects.count()
    response = author_client.post(url, data=form_data_old)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert count_comments_before == (comments_count - 1)
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_anonymous_user_cant_create_comment(client, form_data_old, news):
    url = reverse('news:detail', args=(news.id,))
    comments_before = Comment.objects.count()
    response = client.post(url, data=form_data_old)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comments_before


def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comments_before = Comment.objects.count()
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )

    assert Comment.objects.count() == comments_before


def test_author_can_delete_comment(author_client, news, comment):
    url = reverse('news:detail', args=(news.id,))
    comments_count = Comment.objects.count()
    response = author_client.delete(reverse('news:delete', args=(comment.id,)))
    assertRedirects(response, url + '#comments')
    assert Comment.objects.count() == (comments_count - 1)


def test_user_cant_delete_comment_of_another_user(
    news, not_author_client, comment
):
    comments_count = Comment.objects.count()
    response = not_author_client.delete(
        reverse('news:delete', args=(comment.id,))
    )
    comments_count = Comment.objects.count()
    assert comments_count == Comment.objects.count()


def test_author_can_edit_comment(author_client, news, comment, form_data_new):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(
        reverse('news:edit', args=(comment.id,)), data=form_data_new)
    assertRedirects(response, url + '#comments')
    comm = Comment.objects.get(id=comment.id)
    assert comm.text == form_data_new['text']


def test_user_cant_edit_comment_of_another_user(
    not_author_client, news, comment, form_data_old, form_data_new
):
    response = not_author_client.post(
        reverse('news:edit', args=(comment.id,)), data=form_data_new
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comm = Comment.objects.get(id=comment.id)
    assert comm.text == form_data_old['text']
