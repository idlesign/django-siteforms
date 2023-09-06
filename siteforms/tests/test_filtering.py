from datetime import date

from siteforms.composers.base import FormComposer
from siteforms.tests.testapp.models import Thing
from siteforms.toolbox import FilteringModelForm, FilteringForm, fields


def test_basics(form, request_get):

    thing1 = Thing(fchar='1234', ftext='onetwo', fchoices='one', fdate=date(2023, 9, 1))
    thing1.save()

    thing2 = Thing(fchar='4567', ftext='three', fchoices='one', fdate=date(2023, 9, 5))
    thing2.save()

    thing3 = Thing(fchar='1234', ftext='TWOmore')
    thing3.save()

    things = Thing.objects.all()
    assert len(things) == 3

    class MyModelForm(FilteringModelForm):

        filtering_rules = {
            'ftext': 'icontains',
        }

        class Composer(FormComposer):
            ...

        class Meta:
            model = Thing
            fields = ['fchar', 'ftext', 'fchoices']

    def apply_filter(form_cls,get_str):
        result = form_cls(
            request=request_get(f'some?__submit=siteform&{get_str}'),
            src='GET',
        ).filtering_apply(things)
        return result

    # no relevant for fchar; ftext is ignored
    things_some, applied = apply_filter(MyModelForm, 'fchar=some&ftext=')
    assert len(things_some) == 0
    assert applied

    # one relevant for fchar; ftext is ignored
    things_some, applied = apply_filter(MyModelForm, 'fchar=4567&ftext=')
    assert len(things_some) == 1
    assert things_some.first() == thing2
    assert applied

    # two relevant for ftext (__icontains); fchar is ignored
    things_some, applied = apply_filter(MyModelForm, 'fchar=&ftext=TWO')
    assert len(things_some) == 2
    assert set(things_some) == {thing1, thing3}
    assert applied

    # invalid choice for fchoices -- no filtering
    things_some, applied = apply_filter(MyModelForm, 'fchoices=bogus')
    assert len(things_some) == 3
    assert not applied

    # valid choice for fchoices -- filtered
    things_some, applied = apply_filter(MyModelForm, 'fchoices=one')
    assert len(things_some) == 2
    assert set(things_some) == {thing1, thing2}
    assert applied

    class MyForm(FilteringForm):
        fchoices = fields.MultipleChoiceField(label='fchoices', choices=Thing.CHOICES1.items())

        fdate_from = fields.DateField(label='fdate_from')
        fdate_till = fields.DateField(label='fdate_till')

        lookup_names = {
            'fdate_from': 'fdate',
            'fdate_till': 'fdate',
        }

        filtering_rules = {
            'fchoices': 'in',
            'fdate_from': 'gte',
            'fdate_till': 'lte',
        }

        class Composer(FormComposer):
            ...

    thing4= Thing(fchar='1', fchoices='two', fdate=date(2023, 9, 8))
    thing4.save()

    things = Thing.objects.all()

    # two filters for fdate
    things_some, applied = apply_filter(MyForm, 'fdate_from=2023-09-01&fdate_till=2023-09-06')
    assert len(things_some) == 2
    assert set(things_some) == {thing1, thing2}
    assert applied

    # multiple choice for fchoices
    things_some, applied = apply_filter(MyForm, 'fchoices=one&fchoices=two')
    assert len(things_some) == 3
    assert set(things_some) == {thing1, thing2, thing4}
    assert applied
