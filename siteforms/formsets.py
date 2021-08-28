from django.forms import BaseFormSet, BaseModelFormSet


class SiteformFormSetMixin(BaseFormSet):
    """Custom formset to allow fields rendering subform to have multiple forms."""

    def render(self):
        return f'{self.management_form}' + ('\n'.join(form.render() for form in self))


class ModelFormSet(SiteformFormSetMixin, BaseModelFormSet):
    """Formset for model forms."""
