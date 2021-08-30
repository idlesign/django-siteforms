from siteforms.tests.testapp.models import Thing, Another
from siteforms.toolbox import ReadOnlyWidget


def test_basic(form):

    class MyWidget(ReadOnlyWidget):

        template_name = 'mywidget.html'

    form_cls = form(
        model=Thing,
        readonly_fields={'fchar', 'fforeign', 'fchoices'},
        fields=['fchar', 'ftext', 'fforeign', 'fchoices'],
        model_meta={
            'widgets': {
                'ftext': MyWidget,
            }
        },
    )
    foreign = Another.objects.create(fsome='that')
    thing = Thing.objects.create(fchar='one', ftext='duo', fforeign=foreign, fchoices='q')
    form = form_cls(instance=thing)

    html = f'{form}'
    assert 'one</div>' in html  # Simple readonly
    assert 'that</div>' in html  # FK
    assert '&lt;unknown (q)&gt;</div>' in html  # Unknown in choices
    assert 'mywidgetdata' in html  # data from template
