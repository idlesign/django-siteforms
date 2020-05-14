from typing import Type, Set, Dict

from django.forms import ModelForm as _ModelForm, Form as _Form, HiddenInput, BaseForm
from django.forms import fields  # noqa
from django.http import HttpRequest
from django.utils.safestring import mark_safe

from .widgets import SubformWidget  # noqa

if False:  # pragma: nocover
    from .composers.base import FormComposer  # noqa


class SiteformsMixin(BaseForm):
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

        self.disabled_fields = set(kwargs.pop('disabled_fields', None) or [])
        self.hidden_fields = set(kwargs.pop('hidden_fields', None) or [])

        self.subforms: Dict[str, 'SiteformsMixin'] = {}
        """Allows sub forms registration."""

        self._initialize(kwargs)

        super().__init__(*args, **kwargs)

    def _initialize(self, kwargs):
        # NB: mutates kwargs

        src = self.src
        request = self.request

        # Try to load data from custom course if no model instance provided.
        instance = kwargs.get('instance')

        is_submitted = False

        if not instance and (src and request):
            data = getattr(request, src)
            is_submitted = self.Composer.opt_submit_name in data

            self.is_submitted = is_submitted

            if is_submitted and request.method == src:
                kwargs['data'] = data

        self._initialize_subforms(is_submitted, kwargs)

    def _initialize_subforms(self, is_submitted, kwargs):

        subforms = {}

        for field in self.base_fields.values():
            widget = field.widget
            if isinstance(widget, SubformWidget):
                subforms[widget.alias] = widget.form

        # Instantiate subform classes with the same arguments.
        for alias, subform in subforms.items():

            # Attach Composer automatically if none in subform.
            composer = getattr(subform, 'Composer', None)

            if composer is None:
                setattr(subform, 'Composer', type('DynamicComposer', self.Composer.__bases__, {}))

            subform.Composer.opt_render_form = False

            sub = subform(**{**kwargs, 'prefix': alias})
            sub.is_submitted = is_submitted

            subforms[alias] = sub

        self.subforms = subforms

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
