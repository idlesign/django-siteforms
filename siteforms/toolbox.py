from typing import Type, Set

from django.forms import ModelForm as _ModelForm
from django.utils.safestring import mark_safe

if False:  # pragma: nocover
    from .composers.base import FormComposer  # noqa


class SiteformsMixin:
    """Mixin to extend native Django form tools."""

    disabled_fields: Set[str] = None
    """Fields to be disabled."""

    Composer: Type['FormComposer'] = None

    def __init__(self, *args, request=None, src=None, **kwargs):
        self.src = src
        self.request = request

        if src and request:
            kwargs['data'] = getattr(request, src)

        super().__init__(*args, **kwargs)

    def render(self):
        disabled_fields = set(self.disabled_fields or [])
        self.disabled_fields = disabled_fields

        # Apply disabled.
        for field_name in disabled_fields:
            field = self.fields[field_name]
            field.disabled = True

        return mark_safe(self.Composer(self).render())

    def __str__(self):
        return self.render()


class ModelForm(SiteformsMixin, _ModelForm):
    """Base model form with siteforms features enabled."""
