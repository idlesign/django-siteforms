from django.forms import BoundField


class CustomBoundField(BoundField):
    """This custom bound field allows widgets to access the field itself."""

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        widget = widget or self.field.widget
        widget.bound_field = self
        return super().as_widget(widget, attrs, only_initial)
