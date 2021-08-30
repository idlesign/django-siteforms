from django.forms import ModelForm as _ModelForm, Form as _Form
from django.forms import fields  # noqa exposed for convenience

from .base import SiteformsMixin as _Mixin
from .metas import BaseMeta as _BaseMeta, ModelBaseMeta as _ModelBaseMeta
from .widgets import ReadOnlyWidget  # noqa


class Form(_Mixin, _Form, metaclass=_BaseMeta):
    """Base form with siteforms features enabled."""


class ModelForm(_Mixin, _ModelForm, metaclass=_ModelBaseMeta):
    """Base model form with siteforms features enabled."""

    def save(self, commit=True):

        for subform in self._iter_subforms():

            # Model form can include other types of forms.
            save_method = getattr(subform, 'save', None)
            if save_method:
                save_method(commit=commit)

        return super().save(commit)
