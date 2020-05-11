from siteforms.composers.bootstrap4 import Bootstrap4
from siteforms.tests.testapp.models import Thing
from siteforms.toolbox import ModelForm


class ThingForm(ModelForm):

    class Composer(Bootstrap4):
        """"""

    class Meta:
        model = Thing
        fields = '__all__'


def test_bs4_basic(form_fixture_match):

    thing = Thing()
    thing.save()

    form = ThingForm(instance=thing)

    form_fixture_match(form, 'bs4_basic_1.html')
