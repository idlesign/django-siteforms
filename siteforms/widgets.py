from django.forms import Widget


if False:  # pragma: nocover
    from .fields import CustomBoundField  # noqa
    from .toolbox import SiteformsMixin


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


class ReadOnlyWidget(Widget):
    """Can be used to swap form input element with a field value.
    Useful to make cheap entity details pages by a simple reuse of forms from entity edit pages.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bound_field: 'CustomBoundField' = None  # bound runtime by CustomBoundField

    def represent_value(self, value):

        field = self.bound_field.field

        choices = dict(getattr(field, 'choices', {}))
        if choices:
            value = choices.get(value)

        return value

    def render(self, name, value, attrs=None, renderer=None):
        value = self.represent_value(value)
        return f"{'' if value is None else value}"
