from typing import Any

from siteforms.tests.testapp.models import Thing, Another
from siteforms.toolbox import ReadOnlyWidget


def test_basic(form):

    class MyWidget(ReadOnlyWidget):

        template_name = 'mywidget.html'

    class MyMultipleWidget(ReadOnlyWidget):

        def format_value_hook(self, value: Any):
            return 'dumdum'

    form_cls = form(
        model=Thing,
        readonly_fields={'fchar', 'fforeign', 'fchoices', 'fbool', 'fm2m'},
        fields=['fchar', 'ftext', 'fforeign', 'fchoices', 'fbool', 'fm2m'],
        model_meta={
            'widgets': {
                'ftext': MyWidget,
                'fm2m': MyMultipleWidget,
            }
        },
    )
    foreign = Another.objects.create(fsome='that')
    thing = Thing.objects.create(fchar='one', ftext='duo', fforeign=foreign, fchoices='q', fbool=False)
    form = form_cls(instance=thing)

    html = f'{form}'
    assert 'one</div>' in html  # Simple readonly
    assert 'that</div>' in html  # FK
    assert '&lt;unknown (q)&gt;</div>' in html  # Unknown in choices
    assert 'mywidgetdata' in html  # data from template
    assert 'id="id_fbool" disabled>No</div>' in html  # readonly bool
    assert '>dumdum<' in html  # multiple widget
