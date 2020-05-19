from functools import partial

import pytest

from siteforms.composers.bootstrap4 import Bootstrap4
from siteforms.tests.testapp.models import Thing


class Composer(Bootstrap4):
    """"""


@pytest.fixture
def bs4_form_html(form_html):
    return partial(form_html, composer=Composer, model=Thing)


def test_bs4_basic(bs4_form_html, form_fixture_match):

    thing = Thing()
    thing.save()

    html = bs4_form_html({}, instance=thing)

    form_fixture_match(html, 'bs4_basic_1.html')


def test_bs4_size(bs4_form_html):
    html = bs4_form_html(dict(opt_size=Composer.SIZE_SMALL))
    assert 'form-control form-control-sm' in html
    assert 'form-control-file' in html

    html = bs4_form_html(dict(opt_size=Composer.SIZE_LARGE))
    assert 'form-control form-control-lg' in html


def test_bs4_custom_controls(bs4_form_html):
    html = bs4_form_html(dict(opt_custom_controls=True))
    assert 'custom-control' in html
    assert 'custom-control-label' in html
    assert 'custom-control-input' in html
    assert 'custom-select' in html
    assert 'custom-file' in html
    assert 'custom-file-label' in html
    assert 'custom-file-input' in html
    assert 'form-check' not in html


def test_bs4_custom_columns(bs4_form_html, form_fixture_match):
    html = bs4_form_html(dict(opt_columns=True))
    assert 'form-group row' in html
    assert 'class="col-2"' in html
    assert 'class="col-10"' in html
    assert 'col-form-label' in html


def test_bs4_disabled_plaintext(bs4_form_html):
    html = bs4_form_html(disabled_fields={'fchar'})
    assert 'form-control-plaintext' not in html
    assert 'disabled id="id_fchar"' in html

    html = bs4_form_html(dict(opt_disabled_plaintext=True), disabled_fields={'fchar'})
    assert 'form-control-plaintext' in html


def test_bs4_render_labels(bs4_form_html):
    html = bs4_form_html(dict(opt_render_labels=True))
    assert 'position-static' not in html

    html = bs4_form_html(dict(opt_render_labels=False))
    assert 'position-static' in html


def test_bs4_validation(bs4_form_html, request_factory):
    request = request_factory().get('some?__submit=siteform')
    html = bs4_form_html(src='GET', request=request)
    assert 'is-valid' in html
    assert 'is-invalid' in html
    assert 'invalid-feedback' in html


def test_bs4_form_inline(bs4_form_html):
    html = bs4_form_html(dict(opt_form_inline=True))
    assert 'form-inline' in html


def test_bs4_groups(bs4_form_html, layout):
    html = bs4_form_html(layout)
    assert '<legend>MYBasicGroup</legend><div  class="form-row mx-0">' in html
    assert '<legend></legend>' in html  # no-title group
