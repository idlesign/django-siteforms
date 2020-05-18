import json
from typing import Type, Set, Dict, Union

from django.forms import ModelForm as _ModelForm, Form as _Form, HiddenInput, BaseForm
from django.forms import fields  # noqa
from django.http import HttpRequest
from django.utils.safestring import mark_safe

from .widgets import SubformWidget  # noqa

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

    subform_serialize: bool = False
    """Whether to serialize/deserialize value for this subform."""

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

        self._initialize_pre(kwargs)

        super().__init__(*args, **kwargs)

        self._initialize_post()

    def _initialize_pre(self, kwargs):
        # NB: mutates kwargs

        src = self.src
        request = self.request

        is_submitted = False

        if src and request:
            data = getattr(request, src)
            is_submitted = self.Composer.opt_submit_name in data

            self.is_submitted = is_submitted

            if is_submitted and request.method == src:
                kwargs['data'] = data

        self._initialize_subforms(is_submitted, kwargs)

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
        if self.subform_serialize:
            value = json.loads(value)
        self.initial = value

    def get_subform_value(self) -> Union[dict, str]:
        """Returns data for subform widget. Default: dict.

        Override to customize returned value.

        """
        value = self.cleaned_data

        if self.subform_serialize:
            value = json.dumps(value)

        return value

    def _initialize_subforms(self, is_submitted, kwargs):
        kwargs = kwargs.copy()
        kwargs.pop('instance', None)

        siteforms = {}

        for field_name, subform in self.subforms.items():

            field = self.base_fields[field_name]

            # Attach Composer automatically if none in subform.
            composer = getattr(subform, 'Composer', None)

            if composer is None:
                setattr(subform, 'Composer', type('DynamicComposer', self.Composer.__bases__, {}))

            subform.Composer.opt_render_form = False

            # Instantiate subform classes with the same arguments.
            sub = subform(**{**kwargs, 'prefix': field_name})
            sub.is_submitted = is_submitted
            siteforms[field_name] = sub

            field.widget = SubformWidget(subform=sub)

        self._subforms = siteforms

    def is_valid(self):
        valid = super().is_valid()

        for subform in self._subforms.values():
            valid &= subform.is_valid()

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
