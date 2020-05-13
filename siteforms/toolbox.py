from typing import Type, Set

from django.forms import ModelForm as _ModelForm, HiddenInput
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

    def __init__(self, *args, request=None, src=None, **kwargs):
        self.src = src
        self.request = request

        # Try to load data from custom course if no model instance provided.
        instance = kwargs.get('instance')
        if not instance and (src and request):
            kwargs['data'] = getattr(request, src)

        super().__init__(*args, **kwargs)

    def render(self):
        fields = self.fields  # noqa

        disabled_fields = set(self.disabled_fields or [])
        self.disabled_fields = disabled_fields

        hidden_fields = set(self.hidden_fields or [])
        self.hidden_fields = hidden_fields

        # Apply disabled.
        for field_name in disabled_fields:
            field = fields[field_name]
            field.disabled = True

        # Apply hidden.
        for field_name in hidden_fields:
            field = fields[field_name]
            field.widget = HiddenInput()

        return mark_safe(self.Composer(self).render())

    def __str__(self):
        return self.render()


class ModelForm(SiteformsMixin, _ModelForm):
    """Base model form with siteforms features enabled."""
