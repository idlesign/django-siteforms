import pytest
from django.forms import fields

from siteforms.composers.base import FormComposer
from siteforms.tests.testapp.models import Thing, Another, Additional, AnotherThing
from siteforms.toolbox import ModelForm, Form


class Composer(FormComposer):
    """"""


class MyAnotherForm(ModelForm):

    class Meta:
        model = Another
        fields = '__all__'

    class Composer(Composer):

        opt_render_help = False
        opt_render_labels = False


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


class MyAnotherThingForm(ModelForm):

    class Meta:
        model = AnotherThing
        fields = '__all__'

    class Composer(Composer):
        opt_render_help = False


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

    # test not disabled anymore (base fields stay intact)
    form = new_form_cls()
    rendered = f'{form}'
    assert 'disabled id="id_fchoices"' not in rendered
    assert 'disabled id="id_fforeign-fsome"' not in rendered  # in subform


def test_formset_m2m(request_post, request_get, db_queries):

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
    add3 = Additional.objects.create(fnum='kkk')

    thing = Thing.objects.create(fchar='one')
    thing.fm2m.add(add1, add2)

    # get instead of refresh to get brand new objects
    thing = Thing.objects.get(id=thing.id)

    # Check subform is rendered with instance data.
    form = MyFormWithSet(request=request_get(), src='POST', instance=thing)
    html = f'{form}'
    assert 'name="fm2m-TOTAL_FORMS"' in html
    assert '<input type="text" name="fm2m-0-fnum" value="xxx" ' in html
    assert '<input type="text" name="fm2m-1-fnum" value="yyy" ' in html
    assert ' value="kkk"' not in html

    # Check data save.
    form = MyFormWithSet(request=request_post(data={
        'fchar': 'two',
        'fm2m-TOTAL_FORMS': '3',
        'fm2m-INITIAL_FORMS': '2',
        'fm2m-MIN_NUM_FORMS': '0',
        'fm2m-MAX_NUM_FORMS': '1000',
        'fm2m-0-fnum': 'xxz',
        'fm2m-0-id': '1',
        'fm2m-1-fnum': 'yyz',
        'fm2m-1-id': '2',
        'fm2m-2-fnum': 'qqq',
        'fm2m-2-id': '',
        '__submit': 'siteform',
    }), src='POST', instance=thing)

    is_valid = form.is_valid()
    assert is_valid
    form.save()

    thing = Thing.objects.get(id=thing.id)
    assert thing.fchar == 'two'

    add1 = Additional.objects.get(id=add1.id)
    assert add1.fnum == 'xxz'
    add2 = Additional.objects.get(id=add2.id)
    assert add2.fnum == 'yyz'


def test_formset_m2m_nested(request_post, request_get, db_queries):

    class MyAnotherNestedForm(MyAnotherForm):

        subforms = {
            'fadd': MyAdditionalForm,
        }

    class MyFormWithSet(MyAnotherThingForm):

        subforms = {
            'fm2m': MyAnotherNestedForm,
        }

    # form = MyFormWithSet(request=request_get(), src='POST')
    # html = f'{form}'
    # assert 'name="fm2m-0-fadd-fnum" maxlength="5" ' in html

    add1 = Additional.objects.create(fnum='eee')
    add2 = Additional.objects.create(fnum='www')
    another1 = Another.objects.create(fsome='888', fadd=add1)
    another2 = Another.objects.create(fsome='999', fadd=add2)

    thing = AnotherThing.objects.create(fchar='one')
    thing.fm2m.add(another1, another2)

    # get instead of refresh to get brand new objects
    thing = AnotherThing.objects.get(id=thing.id)

    # Check subform is rendered with instance data.
    # form = MyFormWithSet(request=request_get(), src='POST', instance=thing)
    # html = f'{form}'
    # assert 'name="fm2m-TOTAL_FORMS"' in html
    # assert 'name="fm2m-0-fsome" value="888" ' in html
    # assert 'name="fm2m-0-fadd-fnum" value="eee" ' in html

    assert AnotherThing.objects.count() == 1
    assert Another.objects.count() == 2
    assert Additional.objects.count() == 2

    # Check data save.
    form = MyFormWithSet(request=request_post(data={
        'fchar': 'two',
        'fm2m-TOTAL_FORMS': '3',
        'fm2m-INITIAL_FORMS': '2',
        'fm2m-MIN_NUM_FORMS': '0',
        'fm2m-MAX_NUM_FORMS': '1000',
        'fm2m-0-fsome': '888-y',
        'fm2m-0-fadd-fnum': 'eee-y',
        'fm2m-0-id': '1',
        'fm2m-1-fsome': '999-y',
        'fm2m-1-fadd-fnum': 'www-y',
        'fm2m-1-id': '2',
        'fm2m-2-fsome': '666',
        'fm2m-2-fadd-fnum': 'iii-y',
        'fm2m-2-id': '',
        '__submit': 'siteform',
    }), src='POST', instance=thing)

    is_valid = form.is_valid()
    assert is_valid
    form.save()

    # check items are edited and added to DB and m2m
    assert AnotherThing.objects.count() == 1
    assert Another.objects.count() == 3
    assert Additional.objects.count() == 3

    fm2m_items = list(thing.fm2m.all().order_by('id'))
    assert fm2m_items[-1].fsome == '666'
    assert fm2m_items[-1].fadd.fnum == 'iii-y'

    thing = AnotherThing.objects.get(id=thing.id)
    assert thing.fchar == 'two'

    another1 = Another.objects.get(id=another1.id)
    assert another1.fsome == '888-y'
    another2 = Another.objects.get(id=another2.id)
    assert another2.fsome == '999-y'

    add1 = Additional.objects.get(id=add1.id)
    assert add1.fnum == 'eee-y'
    add2 = Additional.objects.get(id=add2.id)
    assert add2.fnum == 'www-y'


def test_fk(request_post, request_get):

    class MyFormWithFk(MyForm):

        subforms = {
            'fforeign': MyAnotherForm,
        }

        class Composer(MyForm.Composer):
            opt_render_help = False

        class Meta(MyForm.Meta):
            fields = ['fchar', 'fforeign']

    form = MyFormWithFk(request=request_get(), src='POST')
    html = f'{form}'
    assert 'Fforeign_name:' in html
    assert 'name="fforeign-fsome" ' in html

    # Add a foreign item.
    foreign = Another.objects.create(fsome='rrr')
    thing = Thing.objects.create(fchar='one', fforeign=foreign)

    # Check subform is rendered.
    form = MyFormWithFk(request=request_get(), src='POST', instance=thing)
    html = f'{form}'
    assert 'name="fchar" value="one" ' in html
    assert 'name="fforeign-fsome" value="rrr"' in html

    # Check data save.
    form = MyFormWithFk(request=request_post(data={
        'fchar': 'two',
        'fforeign-fsome': 'rru',
        '__submit': 'siteform',
    }), src='POST', instance=thing)

    is_valid = form.is_valid()
    assert is_valid

    # get instead of refresh to get brand new objects
    thing = Thing.objects.get(id=thing.id)
    assert thing.fchar == 'one'

    form.save()

    thing = Thing.objects.get(id=thing.id)
    foreign = Another.objects.get(id=foreign.id)

    assert foreign.fsome == 'rru'
    assert thing.fchar == 'two'


def test_fk_nested(request_post, request_get):

    class MyAnotherNestedForm(MyAnotherForm):

        subforms = {
            'fadd': MyAdditionalForm,
        }

    class MyFormWithFkNested(MyForm):

        subforms = {
            'fforeign': MyAnotherNestedForm,
        }

        class Composer(MyForm.Composer):
            opt_render_help = False

        class Meta(MyForm.Meta):
            fields = ['fchar', 'fforeign']

    form = MyFormWithFkNested(request=request_get(), src='POST')
    html = f'{form}'
    assert 'name="fforeign-fadd-fnum" ' in html

    # Add a foreign item.
    additional = Additional.objects.create(fnum='444')
    foreign = Another.objects.create(fsome='rrr', fadd=additional)
    thing = Thing.objects.create(fchar='one', fforeign=foreign)

    # Check subform is rendered with instance data.
    form = MyFormWithFkNested(request=request_get(), src='POST', instance=thing)
    html = f'{form}'
    assert 'name="fchar" value="one" ' in html
    assert 'name="fforeign-fsome" value="rrr" ' in html
    assert 'name="fforeign-fadd-fnum" value="444" ' in html

    # Check data save.
    form = MyFormWithFkNested(request=request_post(data={
        'fchar': 'two',
        'fforeign-fsome': 'rru',
        'fforeign-fadd-fnum': '555',
        '__submit': 'siteform',
    }), src='POST', instance=thing)

    is_valid = form.is_valid()
    assert is_valid
    form.save()

    thing = Thing.objects.get(id=thing.id)
    foreign = Another.objects.get(id=foreign.id)
    additional = Additional.objects.get(id=additional.id)

    assert foreign.fsome == 'rru'
    assert thing.fchar == 'two'
    assert additional.fnum == '555'

    # check a new foreign
    thing.fforeign = None
    thing.save()

    assert Thing.objects.count() == 1
    assert Another.objects.count() == 1
    assert Additional.objects.count() == 1

    form = MyFormWithFkNested(request=request_post(data={
        'fchar': 'three',
        'fforeign-fsome': 'new',
        'fforeign-fadd-fnum': '777',
        '__submit': 'siteform',
    }), src='POST', instance=thing)

    is_valid = form.is_valid()
    assert is_valid
    assert form.instance.id
    assert form.instance.fchar == 'three'
    assert form.instance.fforeign.id
    assert form.instance.fforeign.fsome == 'new'
    assert form.instance.fforeign.fadd.id
    assert form.instance.fforeign.fadd.fnum == '777'

    assert Thing.objects.count() == 1
    assert Another.objects.count() == 2
    assert Additional.objects.count() == 2


@pytest.fixture
def form_cls(form):

    def form_cls_(*, model=None, use_fields=None):

        class SubForm1(Form):

            first = fields.CharField(label='some', help_text='some help')
            second = fields.ChoiceField(label='variants', choices={'1': 'one', '2': 'two'}.items())

        form_kwargs = dict(
            composer=Composer,
            somefield=fields.CharField(),
            fchar=fields.CharField(max_length=30),
            subforms={'fchar': SubForm1},
            model=model,
            fields=use_fields,
        )
        form_cls = form(**form_kwargs)

        return form_cls

    return form_cls_


def test_json_subforms(form_cls, request_get, request_post):

    def check_source(request, *, instance=None):
        init_kwargs = dict(src=request.method, request=request)

        if instance:
            init_kwargs['instance'] = instance

        form = form_cls(
            model=instance.__class__ if instance else None,
            use_fields=['fchar', 'ftext'],
        )(**init_kwargs)

        is_valid = form.is_valid()

        return is_valid, form

    frm = form_cls()()
    frm_html = f'{frm}'
    assert 'fchar-first' in frm_html

    # Missing field.
    valid, frm = check_source(request_get(
        'some?__submit=siteform&somefield=bc&fchar-second=2'))
    assert not valid
    assert 'field is required.</div></div><small  id="id_fchar-first_help' in f'{frm}'

    # Value is too long for subform field.
    valid, frm = check_source(request_get(
        'some?__submit=siteform&somefield=bc&fchar-second=2&fchar-first=valueistoolong'))
    assert not valid
    assert 'Ensure this value has at most 30' in f'{frm}'

    # All is well.
    valid, frm = check_source(request_get(
        'some?__submit=siteform&somefield=bc&fchar-second=2&fchar-first=op'))
    assert valid
    assert 'field is required' not in f'{frm}'
    assert frm.cleaned_data == {'fchar': '{"first": "op", "second": "2"}', 'somefield': 'bc'}

    # With instance.
    thing = Thing(fchar='{"first": "dum", "second": "2"}', ftext='one')
    thing.save()

    valid, frm = check_source(request_get('some'), instance=thing)
    frm_html = f'{frm}'
    assert 'value="dum"' in frm_html
    assert 'value="2" selected' in frm_html

    # With instance save.
    valid, frm = check_source(request_post(data={
        '__submit': 'siteform',
        'somefield': 'bc',
        'ftext': 'two',
        'fchar-second': '1',
        'fchar-first': 'hi',
    }), instance=thing)

    assert valid
    frm.save()

    # get instead of refresh to get brand new objects
    thing = Thing.objects.get(id=thing.id)
    assert thing.fchar == '{"first": "hi", "second": "1"}'
    assert thing.ftext == 'two'


def test_no_basefields_sideeffect(request_get):

    class MyAnotherNestedForm(MyAnotherForm):

        readonly_fields = '__all__'

        subforms = {
            'fadd': MyAdditionalForm,
        }

    class MyFormWithSet(MyAnotherThingForm):

        subforms = {
            'fm2m': MyAnotherNestedForm,
        }

    add1 = Additional.objects.create(fnum='eee')
    another1 = Another.objects.create(fsome='888', fadd=add1)

    thing = AnotherThing.objects.create(fchar='one')
    thing.fm2m.add(another1)
    thing = AnotherThing.objects.get(id=thing.id)

    form = MyFormWithSet(request=request_get(), src='POST', instance=thing)
    html = f'{form}'
    assert 'id="id_fm2m-0-fsome" disabled>888' in html

    form = MyAnotherForm(request=request_get(), src='POST', instance=another1)
    html = f'{form}'
    assert '" required id="id_fsome"' in html
    assert 'disabled' not in html
