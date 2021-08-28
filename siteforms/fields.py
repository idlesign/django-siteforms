import json
from typing import Optional

from django.forms import BoundField, Field, ModelChoiceField

from .widgets import SubformWidget
from .formsets import BaseFormSet

if False:  # pragma: nocover
    from .base import SiteformsMixin  # noqa


class SubformField(Field):
    """Field representing a subform."""

    widget = SubformWidget

    def __init__(self, *args, original_field, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_field = original_field
        self.form: Optional['SiteformsMixin'] = None

    def get_bound_field(self, form, field_name):
        return SubformBoundField(form, self, field_name)

    def clean(self, value):
        original_field = self.original_field

        if isinstance(original_field, ModelChoiceField):

            if isinstance(self.form, BaseFormSet):
                value = [item['id'].id for item in value if item['id']]  # Skip empty forms

            else:
                # For a subform with a model (FK).
                value = self.form.initial['id']

        else:
            # For a subform with JSON this `value` contains `cleaned_data` dictionary.
            # We convert this into json to allow parent form field to clean it.
            value = json.dumps(value)

        return original_field.clean(value)

    def prepare_value(self, value):
        # prepare value for widget rendering
        return self.original_field.prepare_value(value)

    def to_python(self, value):
        return self.original_field.to_python(value)


class SubformBoundField(BoundField):
    """This custom bound field allows widgets to access the field itself."""

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        widget = widget or self.field.widget
        widget.bound_field = self
        return super().as_widget(widget, attrs, only_initial)
