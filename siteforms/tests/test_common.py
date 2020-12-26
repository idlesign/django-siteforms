from siteforms.composers.base import FormComposer
from siteforms.tests.testapp.models import Thing


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
