from django.forms import BaseFormSet, BaseModelFormSet, BaseInlineFormSet


class SiteformFormSetMixin(BaseFormSet):
    """Custom formset to allow fields rendering subform to have multiple forms."""

    def set_subform_value(self, initial: list):
        """Sets value for a subform."""
        self.initial = initial

    def get_subform_value(self) -> dict:
        """Gets data dict for a subform."""
        return self.cleaned_data

    def render(self):
        return f'{self.management_form}' + ('\n'.join(form.render() for form in self))


class FormSet(SiteformFormSetMixin):
    """Formset for non-model forms."""


class ModelFormSet(SiteformFormSetMixin, BaseModelFormSet):
    """Formset for model forms."""


class InlineFormSet(SiteformFormSetMixin, BaseInlineFormSet):
    """Formset from inlines in model forms."""
