from functools import partial

import pytest

from siteforms.composers.daisyui import Daisyui
from siteforms.tests.testapp.models import Thing


class Composer(Daisyui):
    """"""


@pytest.fixture
def du_form_html(form_html):
    return partial(form_html, composer=Composer, model=Thing)


def test_du_basic(du_form_html, form_fixture_match):

    thing = Thing()
    thing.save()

    html = du_form_html({}, instance=thing)

    form_fixture_match(html, 'du_basic_1.html')


def test_du_size(du_form_html):
    html = du_form_html(dict(opt_size=Composer.SIZE_SMALL))
    assert 'input input-sm' in html
    assert 'btn btn-primary mt-4 btn-sm' in html

    html = du_form_html(dict(opt_size=Composer.SIZE_LARGE))
    assert 'input input-lg' in html
    assert 'select select-lg' in html


def test_du_checkbox_toggle(du_form_html):
    html = du_form_html()
    assert 'class="checkbox"' in html
    assert 'toggle' not in html

    html = du_form_html(dict(opt_checkbox_toggle=True))
    assert 'class="toggle"' in html


def test_du_validation(du_form_html, request_factory):
    request = request_factory().get('some?__submit=siteform')

    html = du_form_html(src='GET', request=request)
    assert 'input-error' in html
    assert 'select-error' in html
    assert 'text-error' in html
    assert '-success' not in html

    html = du_form_html(dict(opt_feedback_valid=True), src='GET', request=request)
    assert '-success' in html
