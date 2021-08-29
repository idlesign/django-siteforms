from typing import Optional, Union

from django.forms import Widget

if False:  # pragma: nocover
    from .fields import SubformBoundField  # noqa
    from .base import TypeSubform


class SubformWidget(Widget):
    """Widget representing a subform"""

    template_name = ''  # Satisfy the interface requirement.

    form: Optional['TypeSubform'] = None
    """Subform or a formset for which the widget is used. 
    Bound runtime by .get_subform().
    
    """

    bound_field: Optional['SubformBoundField'] = None
    """Bound runtime by SubformBoundField when a widget is get."""

    def render(self, name, value, attrs=None, renderer=None):
        # Call form render, or a formset render, or a formset form renderer.
        return self.bound_field.form.get_subform(name=name).render()

    def value_from_datadict(self, data, files, name):
        form = self.form
        if form.is_valid():
            # validate to get the cleaned data
            # that would be used as data for subform
            return form.cleaned_data
        return super().value_from_datadict(data, files, name)


class ReadOnlyWidget(Widget):
    """Can be used to swap form input element with a field value.
    Useful to make cheap entity details pages by a simple reuse of forms from entity edit pages.

    """
    bound_field: 'SubformBoundField' = None
    """Bound runtime."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def represent_value(self, value):

        field = self.bound_field.field

        choices = dict(getattr(field, 'choices', {}))
        if choices:
            value = choices.get(value)

        return value

    def render(self, name, value, attrs=None, renderer=None):
        value = self.represent_value(value)
        return f"{'' if value is None else value}"
