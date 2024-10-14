import pytest

from django.urls import reverse

from django.conf import settings
from news.forms import CommentForm


def test_news_count(client, more_news):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_comments_order(client, news, more_comments):
    response = client.get(reverse('news:detail', args=(news.id,)))
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_news_order(client, more_news, now):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.parametrize(
    'parametrized_client, expected_result',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
def test_clients_has_form(news, parametrized_client, expected_result):
    response = parametrized_client.get(reverse('news:detail', args=(news.id,)))
    assert ('form' in response.context) is expected_result
    if expected_result:
        assert isinstance(response.context['form'], CommentForm)
