import json
from types import MethodType
from typing import Type, Set, Dict, Union

from django.forms import (
    BaseForm,
    formset_factory, modelformset_factory, inlineformset_factory,
    HiddenInput, Field,
)
from django.http import HttpRequest
from django.utils.datastructures import MultiValueDict
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .fields import CustomBoundField
from .formsets import FormSet, ModelFormSet, InlineFormSet, SiteformFormSetMixin
from .widgets import SubformWidget, ReadOnlyWidget

if False:  # pragma: nocover
    from .composers.base import FormComposer  # noqa


UNSET = set()


class SiteformsMixin(BaseForm):
    """Mixin to extend native Django form tools."""

    disabled_fields: Union[Set[str], str] = None
    """Fields to be disabled. Use __all__ to disable all fields (affects subforms).
    
    .. note:: This can also be passed into __init__() as the keyword-argument
        with the same name.
    
    """

    hidden_fields: Set[str] = None
    """Fields to be hidden.
    
    .. note:: This can also be passed into __init__() as the keyword-argument
        with the same name.
    
    """

    readonly_fields: Union[Set[str], str] = None
    """Fields to make read-only. Use __all__ to disable all fields (affects subforms).
    
    .. note:: This can also be passed into __init__() as the keyword-argument
        with the same name.
    
    """

    subforms: Dict[str, Type['SiteformsMixin']] = None
    """Allows sub forms registration. Expects field name to subform class mapping."""

    formset_kwargs: dict = None
    """These kwargs are passed into formsets factory (see `formset_factory()`).
    
    Example::
        {
            'subformfield1': {'extra': 2},
            'subformfield1': {'validate_max': True},
        }

    .. note:: This can also be passed into __init__() as the keyword-argument
        with the same name.
    
    """

    Composer: Type['FormComposer'] = None

    def __init__(
            self,
            *args,
            request: HttpRequest = None,
            src: str = None,
            id: str = '',
            **kwargs
    ):
        """

        :param args:

        :param request: Django request object.

        :param src: Form data source. E.g.: POST, GET.

        :param id: Form ID. If defined the form will be rendered
            with this ID. This ID will also be used as auto_id prefix for fields.

        :param kwargs:

        """
        self.src = src
        self.request = request

        self.is_submitted: bool = False
        """Whether this form is submitted and uses th submitted data."""

        disabled = kwargs.get('disabled_fields', self.disabled_fields)
        self.disabled_fields = disabled if isinstance(disabled, str) else set(disabled or [])

        readonly = kwargs.get('readonly_fields', self.readonly_fields)
        self.readonly_fields = readonly if isinstance(readonly, str) else set(readonly or [])

        self.hidden_fields = set(kwargs.pop('hidden_fields', self.hidden_fields) or [])

        self.formset_kwargs = kwargs.pop('formset_kwargs', self.formset_kwargs) or {}

        self.subforms = kwargs.pop('subforms', self.subforms) or {}

        self.id = id

        if id and 'auto_id' not in kwargs:
            kwargs['auto_id'] = f'{id}_%s'

        self._subforms: Dict[str, Union['SiteformsMixin', 'SiteformFormSetMixin']] = {}

        # Allow subform using the same submit value as the base form.
        self._submit_value = kwargs.pop('submit_value', kwargs.get('prefix', self.prefix) or 'siteform')

        # Need this because the parent initializer
        # is not run yet but they'd required in _initialize_pre().
        self.data = MultiValueDict()
        self.files = MultiValueDict()

        args = list(args)
        self._initialize_pre(args=args, kwargs=kwargs)

        kwargs.pop('disabled_fields', '')
        kwargs.pop('readonly_fields', '')

        super().__init__(*args, **kwargs)

        self._initialize_post()

    def _initialize_pre(self, *, args, kwargs):
        # NB: mutates kwargs

        src = self.src
        request = self.request

        if src and request:
            data = getattr(request, src)
            is_submitted = data.get(self.Composer.opt_submit_name, '') == self._submit_value

            self.is_submitted = is_submitted

            if is_submitted and request.method == src:

                self.data = data
                self.files = request.FILES

                if args:
                    # Prevent arguments clash.
                    args[0] = data

                else:
                    kwargs['data'] = data

        def get_bound_field(self, form, field_name):
            return CustomBoundField(form, self, field_name)

        # todo maybe do it only once?
        for field in self.base_fields.values():
            # Swap bound field to our custom one.
            field.get_bound_field = MethodType(get_bound_field, field)

        self._initialize_subforms(kwargs)

    def _initialize_post(self):

        # Attach files automatically.
        if self.is_submitted and self.is_multipart():
            self.files = self.request.FILES

        initial = self.initial
        for field_name, subform in self._subforms.items():
            subform.is_bound = any((subform.data, subform.files))  # actualize
            initial_value = initial.get(field_name, UNSET)
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
        subforms = self.subforms

        if not subforms:
            return

        kwargs = kwargs.copy()
        kwargs.pop('instance', None)

        kwargs.update({
            'src': self.src,
            'request': self.request,
            'submit_value': self._submit_value,
        })

        subforms_result = {}

        def prepare_value(self, value):
            # convert formset value to satisfy ModelMultipleChoiceField.clean()
            if isinstance(value, list):
                return [item['id'].pk for item in value if item['id']]
            super(self.__class__, self).prepare_value(value)

        base_fields = self.base_fields
        for field_name, subform_cls in subforms.items():

            # Attach Composer automatically if none in subform.
            composer = getattr(subform_cls, 'Composer', None)

            if composer is None:
                setattr(subform_cls, 'Composer', type('DynamicComposer', self.Composer.__bases__, {}))

            subform_cls.Composer.opt_render_form = False

            # todo maybe a compound prefix kwargs['prefix'] = f'{prefix}-{field_name}'

            sub = self._get_subform(
                field_name=field_name,
                subform_cls=subform_cls,
                kwargs_form=kwargs,
            )

            field: Field = base_fields[field_name]
            field.prepare_value = MethodType(prepare_value, field)

            field.widget = SubformWidget(subform=sub)

            subforms_result[field_name] = sub

        self._subforms = subforms_result

    def _get_subform(
            self,
            *,
            field_name: str,
            subform_cls: Type['SiteformsMixin'],
            kwargs_form: dict,
    ):
        # When a field represents a single item (e.g. JSONField).
        return subform_cls(**{**kwargs_form, 'prefix': field_name})

    def _initialize_formset(
            self,
            *,
            field_name: str,
            subform_cls: Type['SiteformsMixin'],
            kwargs_formset: dict,
            kwargs_form: dict,
            mode: str = 'default',
    ) -> SiteformFormSetMixin:
        """Initialize a subform as a fieldset."""

        if mode == 'model':

            factory_cls = modelformset_factory(
                self.base_fields[field_name].queryset.model,
                form=subform_cls,
                formset=ModelFormSet,
                **kwargs_formset
            )

            return factory_cls(
                data=self.data,
                files=self.files,
                prefix=field_name,
                form_kwargs=kwargs_form,
            )

        elif mode == 'inline':
            # todo test it
            factory_cls = inlineformset_factory(
                self.base_fields[field_name].queryset.model,
                self._meta.model,
                form=subform_cls,
                formset=InlineFormSet,
                **kwargs_formset
            )
            return factory_cls(
                data=self.data,
                files=self.files,
                prefix=field_name,
                form_kwargs=kwargs_form,
            )

        factory_cls = formset_factory(subform_cls, formset=FormSet, **kwargs_formset)

        return factory_cls(
            data=self.data,
            files=self.files,
            prefix=field_name,
            form_kwargs=kwargs_form,
        )

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

        disabled = self.disabled_fields
        hidden = self.hidden_fields
        readonly = self.readonly_fields

        all_macro = '__all__'

        for field in self:
            field: CustomBoundField
            field_name = field.name

            if disabled == all_macro or field_name in disabled:
                field.field.disabled = True

            if readonly == all_macro or field_name in readonly:
                field.field.widget = ReadOnlyWidget()

            if field_name in hidden:
                field.field.widget = HiddenInput()

        return mark_safe(self.Composer(self).render())

    def __str__(self):
        return self.render()
