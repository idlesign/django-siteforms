import json
from contextlib import contextmanager
from typing import Type, Set, Dict, Union, Generator, List

from django.forms import (
    BaseForm,
    modelformset_factory, HiddenInput, ModelMultipleChoiceField, ModelChoiceField, Field, )
from django.http import HttpRequest
from django.utils.safestring import mark_safe

from .fields import SubformBoundField
from .formsets import ModelFormSet, SiteformFormSetMixin
from .widgets import ReadOnlyWidget

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
            'subformfield1': {'validate_max': True, 'min_num': 2},
        }

    .. note:: This can also be passed into __init__() as the keyword-argument
        with the same name.
    
    """

    is_submitted: bool = False
    """Whether this form is submitted and uses th submitted data."""

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
        self._subforms_kwargs = {}

        # Allow subform using the same submit value as the base form.
        self._submit_value = kwargs.pop('submit_value', kwargs.get('prefix', self.prefix) or 'siteform')

        args = list(args)
        self._initialize_pre(args=args, kwargs=kwargs)

        kwargs.pop('disabled_fields', '')
        kwargs.pop('readonly_fields', '')

        super().__init__(*args, **kwargs)

        # Attach files automatically.
        if self.is_submitted and self.is_multipart():
            self.files = self.request.FILES

    def __str__(self):
        return self.render()

    def _initialize_pre(self, *, args, kwargs):
        # NB: may mutate args and kwargs

        src = self.src
        request = self.request

        # Handle user supplied data.
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

        if self.subforms:
            # Prepare form arguments.
            subforms_kwargs = kwargs.copy()
            subforms_kwargs.pop('instance', None)

            subforms_kwargs.update({
                'src': self.src,
                'request': self.request,
                'submit_value': self._submit_value,
            })
            self._subforms_kwargs = subforms_kwargs

    def get_subform(self, *, name: str) -> 'SiteformsMixin':

        subform = self._subforms.get(name)

        if not subform:
            subform_cls = self.subforms[name]

            # Attach Composer automatically if none in subform.
            if getattr(subform_cls, 'Composer', None) is None:
                setattr(subform_cls, 'Composer', type('DynamicComposer', self.Composer.__bases__, {}))

            subform_cls.Composer.opt_render_form = False

            kwargs_form = self._subforms_kwargs.copy()

            subform = self._spawn_subform(
                name=name,
                subform_cls=subform_cls,
                kwargs_form=kwargs_form,
            )

            self._subforms[name] = subform

            # Set relevant field form attributes
            # to have form access from other entities.
            field = self.fields[name]
            field.widget.form = subform
            field.form = subform

        return subform

    def _spawn_subform(
            self,
            *,
            name: str,
            subform_cls: Type['SiteformsMixin'],
            kwargs_form: dict,
    ) -> Union['SiteformsMixin', 'SiteformFormSetMixin']:

        original_field = self.base_fields[name].original_field
        subform_mode = ''

        # todo check compound prefix for deeply nested forms kwargs['prefix'] = f'{prefix}-{field_name}'

        if hasattr(original_field, 'queryset'):
            # Possibly a field represents FK or M2M.

            if isinstance(original_field, ModelMultipleChoiceField):
                # Many-to-many.

                formset_cls = modelformset_factory(
                    original_field.queryset.model,
                    form=subform_cls,
                    formset=ModelFormSet,
                    **self.formset_kwargs.get(name, {}),
                )

                queryset = None
                instance = getattr(self, 'instance', None)

                if instance:
                    if instance.pk:
                        queryset = getattr(instance, name).all()
                    else:
                        queryset = original_field.queryset.none()

                return formset_cls(
                    data=self.data or None,
                    files=self.files or None,
                    prefix=name,
                    form_kwargs=kwargs_form,
                    queryset=queryset,
                )

            elif isinstance(original_field, ModelChoiceField):
                subform_mode = 'fk'

        # Subform for JSON and FK.
        subform = self._spawn_subform_inline(
            name=name,
            subform_cls=subform_cls,
            kwargs_form=kwargs_form,
            mode=subform_mode,
        )

        return subform

    def _spawn_subform_inline(
            self,
            *,
            name: str,
            subform_cls: Type['SiteformsMixin'],
            kwargs_form: dict,
            mode: str = '',
    ) -> 'SiteformsMixin':

        mode = mode or 'json'

        initial_value = self.initial.get(name, UNSET)
        instance_value = getattr(getattr(self, 'instance', None), name, UNSET)

        if initial_value is not UNSET:

            if mode == 'json':
                # In case of JSON we get initial from the base form initial by key.
                kwargs_form['initial'] = json.loads(initial_value)

        if instance_value is not UNSET:

            if mode == 'fk':
                kwargs_form.update({
                    'instance': instance_value,
                    'data': self.data or None,
                    'files': self.files or None,
                })

        return subform_cls(**{**kwargs_form, 'prefix': name})

    def _iter_subforms(self) -> Generator['SiteformsMixin', None, None]:
        for name in self.subforms:
            yield self.get_subform(name=name)

    def is_valid(self):
        valid = True

        for subform in self._iter_subforms():
            subform_valid = subform.is_valid()
            valid &= subform_valid

        valid &= super().is_valid()

        return valid

    def render(self) -> str:
        """Renders this form as a string."""

        disabled = self.disabled_fields
        hidden = self.hidden_fields
        readonly = self.readonly_fields

        all_macro = '__all__'

        def store_restore(base_field: Field, attrs: List[str]):
            """Since Django's BoundField uses form base field attributes,
            but not its own (e.g. for disabled in .build_widget_attrs()
            we are forced to store and restore previous values to not to have side
            effects on form classes reuse.

            :param base_field:
            :param attrs:

            """
            for attr in attrs:
                # restore
                tmp_attr = f'_{attr}'
                val = getattr(base_field, tmp_attr, None)

                if val is not None:
                    setattr(base_field, attr, val)
                    delattr(base_field, tmp_attr)

                else:
                    setattr(base_field, f'_{attr}', getattr(base_field, attr))

        mutated_fields = ['disabled', 'widget']

        for field in self:
            field: SubformBoundField
            field_name = field.name

            base_field = field.field
            store_restore(base_field, mutated_fields)

            if disabled == all_macro or field_name in disabled:
                base_field.disabled = True

            if readonly == all_macro or field_name in readonly:
                base_field.widget = ReadOnlyWidget()

            if field_name in hidden:
                base_field.widget = HiddenInput()

        return mark_safe(self.Composer(self).render())
