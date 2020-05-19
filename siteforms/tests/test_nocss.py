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


@pytest.fixture
def form_cls(form):

    def form_cls_(model=None):

        class SubForm1(Form):

            first = fields.CharField(label='some', help_text='some help')
            second = fields.ChoiceField(label='variants', choices={'1': 'one', '2': 'two'}.items())

        form_kwargs = dict(
            composer=Composer,
            somefield=fields.CharField(),
            fchar=fields.CharField(max_length=30),
            subforms={'fchar': SubForm1},
            model=model,
        )
        form_cls = form(**form_kwargs)

        return form_cls

    return form_cls_


def test_nocss_subforms(form_cls, request_factory):

    frm = form_cls()()
    frm_html = f'{frm}'
    assert 'fchar-first' in frm_html

    def check_source(params, *, instance=None):
        request = request_factory().get(params)
        init_kwargs = dict(src='GET', request=request)
        if instance:
            init_kwargs['instance'] = instance
        frm = form_cls(model=instance.__class__ if instance else None)(**init_kwargs)
        valid = frm.is_valid()
        return valid, frm

    # Missing field.
    valid, frm = check_source('some?__submit=siteform&somefield=bc&fchar-second=2')
    assert not valid
    assert 'field is required.</div></div><small  id="id_fchar-first_help' in f'{frm}'

    # Value is too long for subform field.
    valid, frm = check_source('some?__submit=siteform&somefield=bc&fchar-second=2&fchar-first=valueistoolong')
    assert not valid
    assert 'Subform field "fchar": Ensure this value has at most 30' in f'{frm}'

    # All is well.
    valid, frm = check_source('some?__submit=siteform&somefield=bc&fchar-second=2&fchar-first=op')
    assert valid
    assert 'field is required' not in f'{frm}'

    assert frm.cleaned_data == {'fchar': '{"first": "op", "second": "2"}', 'somefield': 'bc'}

    # With instance.
    thing = Thing(fchar='{"first": "dum", "second": "2"}',)
    thing.save()

    valid, frm = check_source('some', instance=thing)
    frm_html = f'{frm}'
    assert 'value="dum"' in frm_html
    assert 'value="2" selected' in frm_html
