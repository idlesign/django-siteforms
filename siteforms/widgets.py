from typing import Optional, Any

from django.forms import Widget, ModelChoiceField
from django.forms.utils import flatatt
from django.utils.translation import gettext_lazy as _

from .utils import UNSET

if False:  # pragma: nocover
    from .fields import SubformBoundField  # noqa
    from .base import TypeSubform


class SubformWidget(Widget):
    """Widget representing a subform"""

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
    template_name = ''

    def __init__(
            self,
            *args,
            bound_field: 'SubformBoundField' = None,
            original_widget: Widget = None,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.bound_field = bound_field
        self.original_widget = original_widget

    def format_value_hook(self, value: Any):
        """Allows format value customization right before it's formatted by base format function."""
        return value

    def format_value(self, value):

        bound_field = self.bound_field
        field = bound_field.field
        use_original_value_format = True

        if isinstance(field, ModelChoiceField):
            # Do not try to pick all choices for FK.
            value = getattr(bound_field.form.instance, bound_field.name, None)
            use_original_value_format = False

        else:
            choices = getattr(field, 'choices', UNSET)
            if choices is not UNSET:
                # Try ro represent a choice value.
                use_original_value_format = False
                if value is not None:
                    # Do not try to get title for None.
                    unknown = _('unknown')
                    value = dict(choices or {}).get(value, f'&lt;{unknown} ({value})&gt;')

        if use_original_value_format:
            original_widget = self.original_widget
            if original_widget:
                value = original_widget.format_value(value)

        value = self.format_value_hook(value)

        return super().format_value(value) or ''

    def _render(self, template_name, context, renderer=None):
        widget_data = context['widget']

        if template_name:
            # Support template rendering for subclasses.
            value = super()._render(template_name, context, renderer)

        else:
            value = widget_data['value']

        return self.wrap_value(value=value, attrs=widget_data['attrs'])

    @classmethod
    def wrap_value(cls, *, value: Any, attrs: dict):
        return f"<div {flatatt(attrs)}>{value}</div>"
