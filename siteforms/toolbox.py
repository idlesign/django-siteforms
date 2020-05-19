import json
from typing import Type, Set, Dict, Union

from django.forms import ModelForm as _ModelForm, Form as _Form, HiddenInput, BaseForm
from django.forms import fields  # noqa
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .widgets import SubformWidget

if False:  # pragma: nocover
    from .composers.base import FormComposer  # noqa


UNSET = set()


class SiteformsMixin(BaseForm):
    """Mixin to extend native Django form tools."""

    disabled_fields: Set[str] = None
    """Fields to be disabled."""

    hidden_fields: Set[str] = None
    """Fields to be hidden."""

    subforms: Dict[str, Type['SiteformsMixin']] = None
    """Allows sub forms registration. Expects field name to subform class mapping."""

    Composer: Type['FormComposer'] = None

    def __init__(
            self,
            *args,
            request: HttpRequest = None,
            src: str = None,
            **kwargs
    ):
        self.src = src
        """Form data source. E.g.: POST, GET."""

        self.request = request
        """Django request object."""

        self.is_submitted: bool = False
        """Whether this form is submitted and uses th submitted data."""

        self.disabled_fields = set(kwargs.pop('disabled_fields', self.disabled_fields) or [])
        self.hidden_fields = set(kwargs.pop('hidden_fields', self.hidden_fields) or [])
        self.subforms = kwargs.pop('subforms', self.subforms) or {}
        self._subforms: Dict[str, 'SiteformsMixin'] = {}

        # Allow subform using the same submit value as the base form.
        self._submit_value = kwargs.pop('submit_value', kwargs.get('prefix', self.prefix) or 'siteform')

        self._initialize_pre(kwargs)

        super().__init__(*args, **kwargs)

        self._initialize_post()

    def _initialize_pre(self, kwargs):
        # NB: mutates kwargs

        src = self.src
        request = self.request

        if src and request:
            data = getattr(request, src)
            is_submitted = data.get(self.Composer.opt_submit_name, '') == self._submit_value

            self.is_submitted = is_submitted

            if is_submitted and request.method == src:
                kwargs['data'] = data

        self._initialize_subforms(kwargs)

    def _initialize_post(self):
        # Attach files automatically.

        if self.is_submitted and self.is_multipart():
            self.files = self.request.FILES

        for field_name, subform in self._subforms.items():
            initial_value = self.initial.get(field_name, UNSET)
            if initial_value is not UNSET:
                subform.set_subform_value(initial_value)

    def set_subform_value(self, value: Union[dict, str]):
        """Sets value for subform."""
        if isinstance(value, str):
            value = json.loads(value)
        self.initial = value

    def get_subform_value(self) -> dict:
        """Returns data dict for subform widget."""
        value = self.cleaned_data

        if isinstance(value, dict):
            value = json.dumps(value)

        return value

    def _initialize_subforms(self, kwargs):
        kwargs = kwargs.copy()
        kwargs.pop('instance', None)

        kwargs.update({
            'src': self.src,
            'request': self.request,
            'submit_value': self._submit_value,
        })

        subforms = {}

        for field_name, subform in self.subforms.items():

            field = self.base_fields[field_name]

            # Attach Composer automatically if none in subform.
            composer = getattr(subform, 'Composer', None)

            if composer is None:
                setattr(subform, 'Composer', type('DynamicComposer', self.Composer.__bases__, {}))

            subform.Composer.opt_render_form = False

            # Instantiate subform classes with the same arguments.
            sub = subform(**{**kwargs, 'prefix': field_name})
            subforms[field_name] = sub

            field.widget = SubformWidget(subform=sub)

        self._subforms = subforms

    def is_valid(self):
        valid = super().is_valid()

        errors = self.errors

        for fieldname, subform in self._subforms.items():
            subform_valid = subform.is_valid()
            valid &= subform_valid

            if subform_valid:
                for error in errors.get(fieldname, []):
                    self.add_error(
                        None,
                        _('Subform field "%(name)s": %(error)s') %
                        {'name': fieldname, 'error': str(error)})

        return valid

    def render(self):
        fields = self.fields

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


class Form(SiteformsMixin, _Form):
    """Base form with siteforms features enabled."""


class ModelForm(SiteformsMixin, _ModelForm):
    """Base model form with siteforms features enabled."""
