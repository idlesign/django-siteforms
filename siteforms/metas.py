from types import MethodType

from django.forms import Field
from django.forms.forms import DeclarativeFieldsMetaclass
from django.forms.models import ModelFormMetaclass

from .base import SiteformsMixin
from .fields import SubformField


class BaseMeta(DeclarativeFieldsMetaclass):

    def __new__(mcs, name, bases, attrs):
        cls: SiteformsMixin = super().__new__(mcs, name, bases, attrs)

        subforms = cls.subforms or {}
        base_fields = cls.base_fields

        for field_name, field in base_fields.items():
            field: Field
            # Swap bound field to our custom one
            # to add .bound_field attr to every widget.
            field.get_bound_field = MethodType(SubformField.get_bound_field, field)

            # Use custom field for subforms.
            if subforms.get(field_name):
                base_fields[field_name] = SubformField(
                    original_field=field,
                    validators=field.validators,
                )

        return cls


class ModelBaseMeta(BaseMeta, ModelFormMetaclass):
    pass
