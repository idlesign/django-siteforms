from siteforms.composers.base import FormComposer
from siteforms.tests.testapp.models import Thing, Another
from siteforms.toolbox import ModelForm


class Composer(FormComposer):
    """"""


class MyAnotherForm(ModelForm):

    class Meta:
        model = Another
        fields = '__all__'

    class Composer(Composer):
        pass


class MyForm(ModelForm):

    class Meta:
        model = Thing
        fields = '__all__'

    class Composer(Composer):
        pass


def test_id(form_html):

    thing = Thing()
    thing.save()

    html = str(form_html(
        composer=Composer, model=Thing,
        id='dum', instance=thing,
    ))
    assert ' id="dum"' in html
    assert ' id="dum_fchar"' in html


def test_args_data(form_html, request_post):

    thing = Thing()
    thing.save()

    form = MyForm({'fchar': '1'}, src='POST', request=request_post(data={
        '__submit': 'siteform',
        'fchar': '2',
    }))

    # automatic `src` handling overrides `data` as the first arg
    assert form.data['fchar'] == '2'


def test_fields_disabled_all():

    new_form_cls = type('MyFormWithSubform', (MyForm,), {
        'subforms': {'fforeign': MyAnotherForm},
    })

    form = new_form_cls(disabled_fields='__all__')
    rendered = f'{form}'
    assert 'disabled id="id_fchoices"' in rendered
    assert 'disabled id="id_fforeign-fsome"' in rendered  # in subform
