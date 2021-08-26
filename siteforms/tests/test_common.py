from siteforms.composers.base import FormComposer
from siteforms.tests.testapp.models import Thing, Another, Additional
from siteforms.toolbox import ModelForm


class Composer(FormComposer):
    """"""


class MyAnotherForm(ModelForm):

    class Meta:
        model = Another
        fields = '__all__'

    class Composer(Composer):
        pass


class MyAdditionalForm(ModelForm):

    class Meta:
        model = Additional
        fields = '__all__'

    class Composer(Composer):
        opt_render_help = False
        opt_render_labels = False


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


def test_args_data(request_post):

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


def test_formsets(request_post, request_get):

    class MyFormWithSet(MyForm):

        subforms = {
            'fm2m': MyAdditionalForm,
        }

        class Composer(MyForm.Composer):
            opt_render_help = False

        class Meta(MyForm.Meta):
            fields = ['fchar', 'fm2m']

    form = MyFormWithSet(request=request_get(), src='POST')
    html = f'{form}'
    expected = '<input type="text" name="fm2m-0-fnum" maxlength="5" aria-label="Fnum_name" id="id_fm2m-0-fnum">'
    assert expected in html

    # Add two m2m items.
    add1 = Additional.objects.create(fnum='xxx')
    add2 = Additional.objects.create(fnum='yyy')
    thing = Thing.objects.create(fchar='one')
    thing.fm2m.add(add1, add2)

    # Check subform is rendered.
    form = MyFormWithSet(request=request_get(), src='POST')
    html = f'{form}'
    assert 'name="fm2m-TOTAL_FORMS"' in html
    assert '<input type="text" name="fm2m-0-fnum" value="xxx" ' in html
    assert '<input type="text" name="fm2m-1-fnum" value="yyy" ' in html

    form = MyFormWithSet(request=request_post(data={
        'fchar': 'two',
        'fm2m-TOTAL_FORMS': '3',
        'fm2m-INITIAL_FORMS': '2',
        'fm2m-MIN_NUM_FORMS': '0',
        'fm2m-MAX_NUM_FORMS': '1000',
        'fm2m-0-fnum': 'xxz',
        'fm2m-0-id': '1',
        'fm2m-1-fnum': 'xxz',
        'fm2m-1-id': '2',
        'fm2m-2-fnum': 'qqq',
        'fm2m-2-id': '',
        '__submit': 'siteform',
    }), src='POST', instance=thing)

    is_valid = form.is_valid()
    assert is_valid
    form.save()

    thing.refresh_from_db()
    assert thing.fchar == 'two'

    add1.refresh_from_db()

    a = 1
