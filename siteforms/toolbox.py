from typing import Type

from django.core.exceptions import FieldDoesNotExist as _FieldDoesNotExist
from django.db.models import ForeignKey as _ForeignKey
from django.forms import ModelForm as _ModelForm, Form as _Form
from django.forms import fields  # noqa exposed for convenience

from .base import SiteformsMixin as _Mixin


class Form(_Mixin, _Form):
    """Base form with siteforms features enabled."""


class ModelForm(_Mixin, _ModelForm):
    """Base model form with siteforms features enabled."""

    def _get_subform(self, *, field_name: str, subform_cls: Type['_Mixin'], kwargs_form: dict):
        # When a field represents several forms (e.g. many-to-many).

        base_field = self.base_fields[field_name]

        if hasattr(base_field, 'queryset'):

            formset_kwargs = self.formset_kwargs.get(field_name, {})
            mode = 'model'
            use_formset = True

            try:
                model_field = self._meta.model._meta.get_field(field_name)

                if isinstance(model_field, _ForeignKey):
                    # mode = 'inline'  todo test it
                    mode = 'default'
                    use_formset = False

            except _FieldDoesNotExist:
                pass

            if use_formset:
                sub = self._initialize_formset(
                    field_name=field_name,
                    subform_cls=subform_cls,
                    kwargs_formset=formset_kwargs,
                    kwargs_form=kwargs_form,
                    mode=mode,
                )
                return sub

        return super()._get_subform(field_name=field_name, subform_cls=subform_cls, kwargs_form=kwargs_form)
