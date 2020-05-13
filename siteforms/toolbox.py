from typing import Type, Set

from django.forms import ModelForm as _ModelForm, HiddenInput
from django.http import HttpRequest
from django.utils.safestring import mark_safe

if False:  # pragma: nocover
    from .composers.base import FormComposer  # noqa


class SiteformsMixin:
    """Mixin to extend native Django form tools."""

    disabled_fields: Set[str] = None
    """Fields to be disabled."""

    hidden_fields: Set[str] = None
    """Fields to be hidden."""

    Composer: Type['FormComposer'] = None

    def __init__(self, *args, request: HttpRequest = None, src: str = None, **kwargs):

        self.src = src
        """Form data source. E.g.: POST, GET."""

        self.request = request
        """Django request object."""

        self.is_submitted: bool = False
        """Whether this form is submitted and uses th submitted data."""

        # Try to load data from custom course if no model instance provided.
        instance = kwargs.get('instance')
        if not instance and (src and request):
            data = getattr(request, src)
            self.is_submitted = self.Composer.opt_submit_name in data
            kwargs['data'] = data

        self.disabled_fields = set(kwargs.pop('disabled_fields', None) or [])
        self.hidden_fields = set(kwargs.pop('hidden_fields', None) or [])

        super().__init__(*args, **kwargs)

    def render(self):
        fields = self.fields  # noqa

        # Apply disabled.
        for field_name in self.disabled_fields:
            field = fields[field_name]
            field.disabled = True

        # Apply hidden.
        for field_name in self.hidden_fields:
            field = fields[field_name]
            field.widget = HiddenInput()

        return mark_safe(self.Composer(self).render())

    def __str__(self):
        return self.render()


class ModelForm(SiteformsMixin, _ModelForm):
    """Base model form with siteforms features enabled."""
