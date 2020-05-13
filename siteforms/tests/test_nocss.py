import pytest

from siteforms.composers.base import FormComposer, FORM, ALL_FIELDS
from siteforms.tests.testapp.models import Thing


class Composer(FormComposer):
    """"""


@pytest.fixture
def nocss_form_html(model_form):
    def bs_model_form_(options=None, **kwargs):
        form = model_form(model=Thing, composer=Composer, options=options)(**kwargs)
        return f'{form}'
    return bs_model_form_


def test_nocss_basic(nocss_form_html, form_fixture_match):

    thing = Thing()
    thing.save()

    html = nocss_form_html({}, instance=thing)

    form_fixture_match(html, 'nocss_basic_1.html')


def test_nocss_validation(nocss_form_html, request_factory):
    request = request_factory().get('some?__submit=1')
    html = nocss_form_html(src='GET', request=request)
    assert 'csrfmiddlewaretoken' in html
    assert '<div>This field is required.</div>' in html


def test_nocss_aria_described_by(nocss_form_html):
    html = nocss_form_html(dict(opt_render_help=True))
    assert 'aria-describedby="id_fbool_help' in html

    html = nocss_form_html(dict(opt_render_help=False))
    assert 'aria-describedby="id_fbool_help' not in html


def test_nocss_placeholders(nocss_form_html):
    html = nocss_form_html(dict(opt_placeholder_label=True))
    assert 'id_fchar_help" placeholder="Fchar_name"' in html

    html = nocss_form_html(dict(opt_placeholder_help=True))
    assert 'id_fchar_help" placeholder="fchar_help"' in html


def test_nocss_disabled_plaintext(nocss_form_html):
    html = nocss_form_html(hidden_fields={'fchar'})
    assert '<input type="hidden" name="fchar" id="id_fchar">' in html


def test_nocss_groups(nocss_form_html, layout):
    html = nocss_form_html(layout)
    assert '<legend>MYBasicGroup</legend>' in html
    assert '</fieldset>\n<fieldset ><legend>somethingmore</legend>' in html
