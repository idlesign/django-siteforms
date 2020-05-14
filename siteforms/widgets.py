import inspect

from django.forms import Widget

if False:  # pragma: nocover
    from siteforms.composers.base import FormComposer  # noqa


class SubformWidget(Widget):
    """Widget representing a subform"""

    template_name = ''

    def __init__(self, form, alias, *, attrs=None):
        super().__init__(attrs)
        self.alias = alias
        self.form = form

    def render(self, name, value, attrs=None, renderer=None):
        composer: 'FormComposer' = inspect.currentframe().f_back.f_back.f_locals['self']
        return composer.form.subforms[self.alias].render()
