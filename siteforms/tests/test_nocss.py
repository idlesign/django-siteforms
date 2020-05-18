from functools import partial

import pytest
from django.forms import fields

from siteforms.composers.base import FormComposer, FORM, ALL_FIELDS
from siteforms.tests.testapp.models import Thing
from siteforms.toolbox import Form


class Composer(FormComposer):
    """"""


@pytest.fixture
def nocss_form_html(form_html):
    return partial(form_html, composer=Composer, model=Thing)


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
    assert '<legend></legend>' in html  # no-title group


def test_nocss_layout_allfields(nocss_form_html):

    layout = {
        'opt_render_labels': False,
        'opt_render_help': False,
        'layout': {
            FORM: {
                'some': [
                    ['fchar', 'fbool'],
                    ALL_FIELDS,
                ],
            },
        },
    }
    html = nocss_form_html(layout)
    assert (
        '</legend><div ><span><input type="text" name="fchar" maxlength="50" aria-label="Fchar_name" '
        'required id="id_fchar"></span>\n<span><input type="checkbox" name="fbool" aria-label="Fbool_name" '
        'id="id_fbool"></span></div>\n<div >' in html)


def test_nocss_nonmultipart(form):
    frm = form(composer=Composer, some=fields.CharField())()
    assert '<form  method="POST">' in f'{frm}'


def test_nocss_subforms(form, request_factory):

    class SubForm1(Form):

        first = fields.CharField(label='some', help_text='some help')
        second = fields.ChoiceField(label='variants', choices={'1': 'one', '2': 'two'}.items())

        def get_subform_value(self):
            value = super().get_subform_value()
            return f"{value['first']}|{value['second']}"

    form_cls = form(
        composer=Composer,
        somefield=fields.CharField(),
        formsub1=fields.CharField(),
        subforms={'formsub1': SubForm1},
    )

    frm = form_cls()
    frm_html = f'{frm}'
    assert 'formsub1-first' in frm_html

    def check_source(params):
        request = request_factory().get(params)
        frm = form_cls(src='GET', request=request)
        valid = frm.is_valid()
        return valid, frm

    valid, frm = check_source('some?__submit=1&somefield=bc&formsub1-second=2')
    assert not valid
    assert 'field is required.</div></span><small  id="id_formsub1-first_help' in f'{frm}'

    valid, frm = check_source('some?__submit=1&somefield=bc&formsub1-second=2&formsub1-first=op')
    assert valid
    assert 'field is required' not in f'{frm}'

    assert frm.cleaned_data == {'somefield': 'bc', 'formsub1': 'op|2'}
