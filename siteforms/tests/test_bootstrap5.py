from functools import partial

import pytest

from siteforms.composers.bootstrap5 import Bootstrap5
from siteforms.tests.testapp.models import Thing


class Composer(Bootstrap5):
    """"""


@pytest.fixture
def bs5_form_html(form_html):
    return partial(form_html, composer=Composer, model=Thing)


def test_bs5_basic(bs5_form_html, form_fixture_match):

    thing = Thing()
    thing.save()

    html = bs5_form_html({}, instance=thing)

    form_fixture_match(html, 'bs5_basic_1.html')


def test_bs5_size(bs5_form_html):
    html = bs5_form_html(dict(opt_size=Composer.SIZE_SMALL))
    assert 'form-control form-control-sm' in html

    html = bs5_form_html(dict(opt_size=Composer.SIZE_LARGE))
    assert 'form-control form-control-lg' in html


def test_bs5_custom_columns(bs5_form_html, form_fixture_match):
    html = bs5_form_html(dict(opt_columns=True))
    assert 'class="col-2"' in html
    assert 'class="col-10"' in html
    assert 'col-form-label' in html


def test_bs5_disabled_plaintext(bs5_form_html):
    html = bs5_form_html(disabled_fields={'fchar'})
    assert 'form-control-plaintext' not in html
    assert 'disabled id="id_fchar"' in html

    html = bs5_form_html(dict(opt_disabled_plaintext=True), disabled_fields={'fchar'})
    assert 'form-control-plaintext' in html


def test_bs5_validation(bs5_form_html, request_factory):
    request = request_factory().get('some?__submit=siteform')
    html = bs5_form_html(src='GET', request=request)
    assert 'is-valid' in html
    assert 'is-invalid' in html
    assert 'invalid-feedback' in html


def test_bs5_form_inline(bs5_form_html):
    html = bs5_form_html(dict(opt_form_inline=True))
    assert 'row row-cols-auto' in html


def test_bs5_labels_floating(bs5_form_html):
    html = bs5_form_html(dict(opt_labels_floating=True))
    assert 'form-floating' in html


def test_bs5_switch(bs5_form_html):
    html = bs5_form_html(dict(opt_checkbox_switch=True))
    assert 'form-switch' in html
