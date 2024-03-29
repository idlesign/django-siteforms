from datetime import date

import pytest
from django.forms import ModelMultipleChoiceField

from siteforms.composers.base import FormComposer, ALL_FIELDS
from siteforms.tests.testapp.models import Thing, Another, Additional, AnotherThing, Link, WithThrough, ThroughModel
from siteforms.toolbox import ModelForm, Form, fields


class Composer(FormComposer):

    opt_render_help = False
    opt_render_labels = False


class ModelFormBase(ModelForm):

    class Composer(Composer):
        pass


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
        pass


class MyForm(ModelForm):

    class Meta:
        model = Thing
        fields = '__all__'

    class Composer(Composer):
        pass


class MyFormWithProperty(MyForm):

    aprop = fields.CharField(label='from property', required=False)

    class Meta(MyForm.Meta):
        property_fields = ['aprop']


class LinkForm(ModelForm):

    subforms = {
        'fthing': MyForm,
    }

    class Meta:
        model = Link
        fields = '__all__'

    class Composer(Composer):
        pass


class MyAnotherThingForm(ModelForm):

    class Meta:
        model = AnotherThing
        fields = '__all__'

    class Composer(Composer):
        pass


def test_append_attr_class():

    class AdditionalWithCss(MyAdditionalForm):

        class Composer(MyAdditionalForm.Composer):
            attrs = {
                ALL_FIELDS: {'class': 'my'},
                'fnum': {'class': '+yours'}
            }

    frm = AdditionalWithCss()
    html = f'{frm}'
    assert 'class="my yours"' in html


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

    form = MyForm(
        {'fchar': '1', 'ftext': 'populated'},
        src='POST',
        request=request_post(data={'__submit': 'siteform', 'fchar': '2', 'fchoices': '2'}),
    )

    # both datas are combined, src-request data has lesser priority
    # automatic `src` handling doesn't override `data` as the first arg or kwarg
    data = form.data.dict()
    assert data['fchar'] == '1'
    assert data['ftext'] == 'populated'
    assert data['fchoices'] == '2'


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

    class MyFormWithSet(MyAnotherThingForm):

        subforms = {
            'fm2m': MyAnotherNestedForm,
        }

    form = MyFormWithSet(request=request_get(), src='POST')
    html = f'{form}'
    assert 'name="fm2m-0-fadd-fnum" maxlength="5" ' in html

    add1 = Additional.objects.create(fnum='eee')
    add2 = Additional.objects.create(fnum='www')
    another1 = Another.objects.create(fsome='888', fadd=add1)
    another2 = Another.objects.create(fsome='999', fadd=add2)

    thing = AnotherThing.objects.create(fchar='one')
    thing.fm2m.add(another1, another2)

    # get instead of refresh to get brand new objects
    thing = AnotherThing.objects.get(id=thing.id)

    # Check subform is rendered with instance data.
    form = MyFormWithSet(request=request_get(), src='POST', instance=thing)
    html = f'{form}'
    assert 'name="fm2m-TOTAL_FORMS"' in html
    assert 'name="fm2m-0-fsome" value="888" ' in html
    assert 'name="fm2m-0-fadd-fnum" value="eee" ' in html
    assert 'fm2m-0-id' in html

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

        class Composer(Composer):
            opt_render_labels = True

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


class MyAnotherNestedForm(MyAnotherForm):

    subforms = {
        'fadd': MyAdditionalForm,
    }


class MyFormWithFkNested(MyForm):

    subforms = {
        'fforeign': MyAnotherNestedForm,
    }

    class Composer(Composer):
        opt_render_labels = True

    class Meta(MyForm.Meta):
        fields = ['fchar', 'fforeign']


def test_fk_nested(request_post, request_get):

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

        class MyComposer(Composer):
            opt_render_help = True

        class SubForm1(Form):

            first = fields.CharField(label='some', help_text='some help')
            second = fields.ChoiceField(label='variants', choices={'1': 'one', '2': 'two'}.items())
            th = fields.DateField(label='date', initial=date(2023, 1, 1), required=False)

        form_kwargs = dict(
            composer=MyComposer,
            somefield=fields.CharField(),
            fchar=fields.CharField(max_length=100),
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
        'some?__submit=siteform&somefield=bc&fchar-second=2&fchar-first=' + ('x' * 300)))
    assert not valid
    assert 'Ensure this value has at most 100' in f'{frm}'

    # All is well.
    valid, frm = check_source(request_get(
        'some?__submit=siteform&somefield=bc&fchar-second=2&fchar-first=op'))
    assert valid
    assert 'field is required' not in f'{frm}'
    assert frm.cleaned_data == {'fchar': '{"first": "op", "second": "2", "th": null}', 'somefield': 'bc'}

    # With instance.
    thing = Thing(fchar='{"first": "dum", "second": "2", "th": "2023-01-02"}', ftext='one')
    thing.save()

    valid, frm = check_source(request_get('some'), instance=thing)
    assert not valid
    frm_html = f'{frm}'
    assert 'value="dum"' in frm_html
    assert 'value="2" selected' in frm_html
    assert 'value="2023-01-02"' in frm_html

    # With instance save.
    valid, frm = check_source(request_post(data={
        '__submit': 'siteform',
        'somefield': 'bc',
        'ftext': 'two',
        'fchar-second': '1',
        'fchar-first': 'hi',
        'fchar-th': '2023-01-03',
    }), instance=thing)

    assert valid
    frm.save()

    # get instead of refresh to get brand new objects
    thing = Thing.objects.get(id=thing.id)
    assert thing.fchar == '{"first": "hi", "second": "1", "th": "2023-01-03"}'
    assert thing.ftext == 'two'


class MyAnotherNestedForm2(MyAnotherForm):

    readonly_fields = '__all__'

    subforms = {
        'fadd': MyAdditionalForm,
    }


class MyFormWithSet(MyAnotherThingForm):

    subforms = {
        'fm2m': MyAnotherNestedForm2,
    }


def test_no_basefields_sideeffect(request_get):

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


def test_cheap_details_view(request_get):

    add1 = Additional.objects.create(fnum='eee')
    another1 = Another.objects.create(fsome='888', fadd=add1)
    another2 = Another.objects.create(fsome='999', fadd=add1)

    thing = AnotherThing.objects.create(fchar='one')
    thing.fm2m.add(another1, another2)

    form = MyFormWithSet(
        request=request_get(), src='POST', instance=thing,
        readonly_fields='__all__', render_form_tag=False)

    html = f'{form}'
    assert 'disabled>999</div>' in html
    assert '<form ' not in html

    nested_form = form.get_subform(name='fm2m').forms[0]
    assert not nested_form.base_fields['fadd'].disabled
    assert nested_form.fields['fadd'].disabled


def test_multipart(request_get):

    form = LinkForm()
    assert form.is_multipart()  # has nested form with FileField


def test_model_with_property():
    mything = Thing(fchar='yes')
    mything.save()

    form = MyFormWithProperty(instance=mything)
    html = f'{form}'
    assert 'value="he-yes"' in html


def test_render_form_tag(form_cls, request_get):

    def spawn(**kwargs):
        return form_cls(model=Thing, use_fields=['fchar', 'ftext'])(**kwargs)

    form = spawn()
    assert '<form ' in f'{form}'

    form = spawn(render_form_tag=False)
    assert '<form ' not in f'{form}'


def test_through(request_get, request_post, get_inputs):

    class ThroughModelForm(ModelFormBase):

        readonly_fields = {'notouch'}

        subforms = {
            'additional': MyAdditionalForm
        }

        class Meta:
            exclude = ['with_through']
            model = ThroughModel

    class WithThroughForm(ModelFormBase):

        through = ModelMultipleChoiceField(queryset=ThroughModel.objects.none())

        formset_kwargs = {
            'through': {'extra': 0}
        }

        subforms = {
            'through': ThroughModelForm
        }

        class Meta:
            fields = '__all__'
            exclude = ['additionals']
            model = WithThrough

        def __init__(self, *args, **kwargs):
            instance = kwargs.get('instance')
            if instance:
                self.base_fields['through'].queryset = ThroughModel.objects.filter(with_through=instance)
            super().__init__(*args, **kwargs)

    with_1 = WithThrough.objects.create(title='with_1')
    with_2 = WithThrough.objects.create(title='with_2')
    add_1 = Additional.objects.create(fnum='18')
    add_2 = Additional.objects.create(fnum='19')
    through_1 = ThroughModel.objects.create(with_through=with_1, additional=add_1, payload='dod', notouch='tut')
    through_2 = ThroughModel.objects.create(with_through=with_2, additional=add_2, payload='aaa', notouch='yyy')

    assert with_1.additionals.count() == 1

    form = WithThroughForm(request=request_get(), instance=with_1)
    html = f'{form}'
    assert '<form' in html

    params = dict(get_inputs(html))
    assert len(params) == 8
    params['__submit'] = 'siteform'
    assert 'through-0-id' in params

    form = WithThroughForm(request=request_post(data=params), instance=with_1, src='POST')
    form.is_valid()
    html = f'{form}'
    assert 'id="id_through-0-id"' in html
