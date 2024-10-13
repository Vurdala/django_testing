import pytest

from django.urls import reverse

from yanews.settings import NEWS_COUNT_ON_HOME_PAGE
from news.forms import CommentForm


def test_news_count(client, more_news):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == NEWS_COUNT_ON_HOME_PAGE


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


def test_anonymous_client_has_no_form(client, news):
    response = client.get(reverse('news:detail', args=(news.id,)))
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news):
    response = author_client.get(reverse('news:detail', args=(news.id,)))
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
