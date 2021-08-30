from functools import partial

import pytest
from django.forms import fields

from siteforms.composers.base import FormComposer, FORM, ALL_FIELDS
from siteforms.tests.testapp.models import Thing


class Composer(FormComposer):
    """"""


@pytest.fixture
def nocss_form_html(form_html):
    return partial(form_html, composer=Composer, model=Thing)


def test_nonfield_errors(form, request_factory):
    request = request_factory().get('some?__submit=siteform&some=hmm')

    frm = form(
        composer=Composer,
        some=fields.DateField(widget=fields.HiddenInput())
    )(src='GET', request=request)

    frm.is_valid()

    frm.add_error(None, 'Errr1')
    frm.add_error(None, 'Errr2')

    form_html = f'{frm}'
    assert '<div ><div>Errr1</div>\n<div>Errr2</div>' in form_html
    assert 'Hidden field "some": Enter a valid date.' in form_html


def test_nocss_basic(nocss_form_html, form_fixture_match):

    thing = Thing()
    thing.save()

    html = nocss_form_html({}, instance=thing)

    form_fixture_match(html, 'nocss_basic_1.html')


def test_nocss_validation(nocss_form_html, request_factory):
    request = request_factory().get('some?__submit=siteform')
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


def test_nocss_title(nocss_form_html):
    html = nocss_form_html(dict(opt_title_label=True))
    assert 'id_fchar_help" title="Fchar_name"' in html

    html = nocss_form_html(dict(opt_title_help=True))
    assert 'id_fchar_help" title="fchar_help"' in html


def test_nocss_hidden(nocss_form_html):
    html = nocss_form_html(hidden_fields={'fchar'})
    assert '<input type="hidden" name="fchar" id="id_fchar">' in html


def test_nocss_disabled(nocss_form_html):
    html = nocss_form_html(disabled_fields={'fchar'})
    assert 'disabled id="id_fchar">' in html


def test_nocss_readonly(nocss_form_html):
    thing = Thing(fchoices='two')
    html = nocss_form_html(readonly_fields={'fchoices'}, instance=thing)
    assert 'id="id_fchoices" disabled required>2</div><small' in html


def test_nocss_groups(nocss_form_html, layout):
    html = nocss_form_html(layout)
    assert '<legend>MYBasicGroup</legend>' in html
    assert '</fieldset>\n<fieldset ><legend>somethingmore</legend>' in html
    assert '<legend></legend>' in html  # no-title group


def test_nocss_layout(nocss_form_html):

    layout = {
        'opt_render_labels': False,
        'opt_render_help': False,
        'layout': {
            FORM: {
                'some': [
                    ['fchar', ['fbool', 'ftext']],
                    ['file'],
                    'fchoices',
                    ALL_FIELDS,
                ],
            },
        },
    }
    html = nocss_form_html(layout)
    assert (
        '<span><input type="text" name="fchar" maxlength="50" aria-label="Fchar_name" required id="id_fchar"></span>\n'
        '<div><span><input type="checkbox" name="fbool" aria-label="Fbool_name" id="id_fbool"></span>\n'
        '<span><textarea name="ftext" cols="40" rows="10" aria-label="Ftext_name" required id="id_ftext">\n'
        '</textarea></span></div></div>' in html)


def test_nocss_nonmultipart(form):
    frm = form(composer=Composer, some=fields.CharField())()
    assert '<form  method="POST">' in f'{frm}'
