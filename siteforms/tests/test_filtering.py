from siteforms.composers.base import FormComposer
from siteforms.tests.testapp.models import Thing
from siteforms.toolbox import ModelForm


def test_basics(form, request_get):

    thing1 = Thing(fchar='1234', ftext='onetwo', fchoices='one')
    thing1.save()

    thing2 = Thing(fchar='4567', ftext='three', fchoices='one')
    thing2.save()

    thing3 = Thing(fchar='1234', ftext='TWOmore')
    thing3.save()

    things = Thing.objects.all()
    assert len(things) == 3

    class MyForm(ModelForm):

        filtering_rules = {
            'ftext': 'icontains',
        }

        class Composer(FormComposer):
            ...

        class Meta:
            model = Thing
            fields = ['fchar', 'ftext', 'fchoices']

    def apply_filter(get_str):
        qs = MyForm(
            request=request_get(f'some?__submit=siteform&{get_str}'),
            src='GET',
        ).filtering_apply(things)
        return qs

    # no relevant for fchar; ftext is ignored
    things_some = apply_filter('fchar=some&ftext=')
    assert len(things_some) == 0

    # one relevant for fchar; ftext is ignored
    things_some = apply_filter('fchar=4567&ftext=')
    assert len(things_some) == 1
    assert things_some.first() == thing2

    # two relevant for ftext (__icontains); fchar is ignored
    things_some = apply_filter('fchar=&ftext=TWO')
    assert len(things_some) == 2
    assert set(things_some) == {thing1, thing3}

    # invalid choice for fchoices -- no filtering
    things_some = apply_filter('fchoices=bogus')
    assert len(things_some) == 3

    # valid choice for fchoices -- no filtering
    things_some = apply_filter('fchoices=one')
    assert len(things_some) == 2
    assert set(things_some) == {thing1, thing2}
