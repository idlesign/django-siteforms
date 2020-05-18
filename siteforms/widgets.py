from django.forms import Widget

if False:  # pragma: nocover
    from siteforms.toolbox import FormComposer, SiteformsMixin  # noqa


class SubformWidget(Widget):
    """Widget representing a subform"""

    template_name = ''  # Obey the requirement.

    def __init__(self, subform: 'SiteformsMixin', *, attrs=None):
        super().__init__(attrs)
        self.subform = subform

    def render(self, name, value, attrs=None, renderer=None):
        return self.subform.render()

    def value_from_datadict(self, data, files, name):
        subform = self.subform
        if subform.is_valid():
            return subform.get_subform_value()
        return None
