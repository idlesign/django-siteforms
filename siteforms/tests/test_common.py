from siteforms.composers.base import FormComposer
from siteforms.tests.testapp.models import Thing
from siteforms.toolbox import ModelForm


class Composer(FormComposer):
    """"""


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

    class MyForm(ModelForm):

        class Meta:
            model = Thing
            fields = ['fchar']

        class Composer(Composer):
            pass

    form = MyForm({'fchar': '1'}, src='POST', request=request_post(data={
        '__submit': 'siteform',
        'fchar': '2',
    }))

    # automatic `src` handling overrides `data` as the first arg
    assert form.data['fchar'] == '2'
