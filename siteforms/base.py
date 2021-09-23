import json
from typing import Type, Set, Dict, Union, Generator, Callable, Any

from django.forms import (
    BaseForm,
    modelformset_factory, HiddenInput,
    ModelMultipleChoiceField, ModelChoiceField, BaseFormSet,
)
from django.http import HttpRequest
from django.utils.safestring import mark_safe

from .fields import SubformBoundField, SubformField
from .formsets import ModelFormSet, SiteformFormSetMixin
from .utils import bind_subform, UNSET, temporary_fields_patch
from .widgets import ReadOnlyWidget

if False:  # pragma: nocover
    from .composers.base import FormComposer, TypeComposer  # noqa


TypeSubform = Union['SiteformsMixin', SiteformFormSetMixin]
TypeDefFieldsAll = Union[Set[str], str]
TypeDefSubforms = Dict[str, Type['SiteformsMixin']]


class SiteformsMixin(BaseForm):
    """Mixin to extend native Django form tools."""

    disabled_fields: TypeDefFieldsAll = None
    """Fields to be disabled. Use __all__ to disable all fields (affects subforms).
    
    .. note:: This can also be passed into __init__() as the keyword-argument
        with the same name.
    
    """

    hidden_fields: Set[str] = None
    """Fields to be hidden.
    
    .. note:: This can also be passed into __init__() as the keyword-argument
        with the same name.
    
    """

    readonly_fields: TypeDefFieldsAll = None
    """Fields to make read-only. Use __all__ to disable all fields (affects subforms).
    Readonly fields are disabled automatically to prevent data corruption.
    
    .. note:: This can also be passed into __init__() as the keyword-argument
        with the same name.
    
    """

    subforms: TypeDefSubforms = None
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
            id: str = '',  # noqa
            parent: 'SiteformsMixin' = None,
            hidden_fields: Set[str] = UNSET,
            formset_kwargs: dict = UNSET,
            subforms: TypeDefSubforms = UNSET,
            submit_marker: Any = UNSET,
            render_form_tag: bool = UNSET,
            **kwargs
    ):
        """

        :param args:

        :param request: Django request object.

        :param src: Form data source. E.g.: POST, GET.

        :param id: Form ID. If defined the form will be rendered
            with this ID. This ID will also be used as auto_id prefix for fields.

        :param parent: Parent form for a subform.

        :param hidden_fields: See the class attribute docstring.

        :param formset_kwargs: See the class attribute docstring.

        :param subforms: See the class attribute docstring.

        :param submit_marker: A value that should be used to detect
            whether the form was submitted.

        :param render_form_tag: Can be used to override `Composer.opt_render_form_tag` setting.
            Useful in conjunction with `readonly_fields='__all__` to make read-only details pages
            using form layout.

        :param kwargs: Form arguments to pass to the base
            class of this form and also to subforms.

        """
        self.src = src
        self.request = request

        disabled = kwargs.get('disabled_fields', self.disabled_fields)
        self.disabled_fields = disabled if isinstance(disabled, str) else set(disabled or [])

        readonly = kwargs.get('readonly_fields', self.readonly_fields)
        self.readonly_fields = readonly if isinstance(readonly, str) else set(readonly or [])

        self.hidden_fields = set((self.hidden_fields if hidden_fields is UNSET else hidden_fields) or [])
        self.formset_kwargs = (self.formset_kwargs if formset_kwargs is UNSET else formset_kwargs) or {}
        self.subforms = (self.subforms if subforms is UNSET else subforms) or {}
        self.composer_render_form_tag = render_form_tag

        self.id = id

        if id and 'auto_id' not in kwargs:
            kwargs['auto_id'] = f'{id}_%s'

        self._subforms: Dict[str, TypeSubform] = {}  # noqa
        self._subforms_kwargs = {}
        self.parent = parent

        # Allow subform using the same submit value as the base form.
        self.submit_marker = (
            (kwargs.get('prefix', self.prefix) or 'siteform')
            if submit_marker is UNSET
            else submit_marker)

        args = list(args)
        self._initialize_pre(args=args, kwargs=kwargs)

        kwargs.pop('disabled_fields', '')
        kwargs.pop('readonly_fields', '')

        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.render()

    def _initialize_pre(self, *, args, kwargs):
        # NB: may mutate args and kwargs

        src = self.src
        request = self.request

        # Handle user supplied data.
        if src and request:
            data = getattr(request, src)
            is_submitted = data.get(self.Composer.opt_submit_name, '') == self.submit_marker

            self.is_submitted = is_submitted

            if is_submitted and request.method == src:

                self.data = data
                files = request.FILES
                self.files = files

                if args:
                    # Prevent arguments clash.
                    args[0] = data
                    if len(args) > 1:
                        args[1] = files

                else:
                    kwargs.update({
                        'data': data,
                        'files': files,
                    })

        if self.subforms:
            # Prepare form arguments.
            subforms_kwargs = kwargs.copy()
            subforms_kwargs.pop('instance', None)

            subforms_kwargs.update({
                'src': self.src,
                'request': self.request,
                'submit_marker': self.submit_marker,
                'parent': self,
            })
            self._subforms_kwargs = subforms_kwargs

    def get_subform(self, *, name: str) -> TypeSubform:
        """Returns a subform instance by its name
        (or possibly a name of a nested subform field, representing a form).

        :param name:

        """
        prefix = self.prefix

        if prefix:
            # Strip down field name prefix to get a form name.
            name = name.replace(prefix, '', 1).lstrip('-')

        subform = self._subforms.get(name)

        if not subform:
            subform_cls = self.subforms[name]

            # Attach Composer automatically if none in subform.
            if getattr(subform_cls, 'Composer', None) is None:
                setattr(subform_cls, 'Composer', type('DynamicComposer', self.Composer.__bases__, {}))

            kwargs_form = self._subforms_kwargs.copy()
            kwargs_form['render_form_tag'] = False

            # Construct a full (including parent prefixes) name prefix
            # to support deeply nested forms.
            if prefix:
                kwargs_form['prefix'] = f'{prefix}-{name}'

            subform = self._spawn_subform(
                name=name,
                subform_cls=subform_cls,
                kwargs_form=kwargs_form,
            )

            self._subforms[name] = subform

            # Set relevant field form attributes
            # to have form access from other entities.
            field = self.fields[name]
            bind_subform(subform=subform, field=field)

        return subform

    def _spawn_subform(
            self,
            *,
            name: str,
            subform_cls: Type['SiteformsMixin'],
            kwargs_form: dict,
    ) -> TypeSubform:

        original_field = self.base_fields[name].original_field
        subform_mode = ''

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

        return subform_cls(**{'prefix': name, **kwargs_form})

    def _iter_subforms(self) -> Generator[TypeSubform, None, None]:
        for name in self.subforms:
            yield self.get_subform(name=name)

    def is_valid(self):

        valid = True

        for subform in self._iter_subforms():
            subform_valid = subform.is_valid()
            valid &= subform_valid

        valid &= super().is_valid()

        return valid

    def get_composer(self) -> 'TypeComposer':
        """Spawns a form composer object.
        Hook method. May be reimplemented by a subclass
        for a further composer modification.
        """
        return self.Composer(self)

    def render(self) -> str:
        """Renders this form as a string."""
        def render_():
            return mark_safe(self.get_composer().render(
                render_form_tag=self.composer_render_form_tag,
            ))
        return self._apply_attrs(callback=render_)

    def is_multipart(self):

        is_multipart = super().is_multipart()

        if is_multipart:
            return True

        for subform in self._iter_subforms():

            if isinstance(subform, BaseFormSet):
                # special case this since Django's implementation
                # won't consider empty form at all.
                if subform.forms:
                    is_multipart = subform.forms[0].is_multipart()

                is_multipart = is_multipart or subform.empty_form.is_multipart()

            else:
                is_multipart = subform.is_multipart()

            if is_multipart:
                break

        return is_multipart

    def _clean_fields(self):
        # this ensures valid attributes on validation including that in formsets
        self._apply_attrs(callback=super()._clean_fields)

    def _apply_attrs(self, callback: Callable):

        disabled = self.disabled_fields
        hidden = self.hidden_fields
        readonly = self.readonly_fields

        all_macro = '__all__'

        with temporary_fields_patch(self):

            for field in self:
                field: SubformBoundField
                field_name = field.name
                base_field = field.field
                instance_field = self.fields[field_name]

                made_readonly = False
                if readonly == all_macro or field_name in readonly:
                    original_widget = base_field.widget

                    make_read_only = (
                        # We do not set this widget if already set, since
                        # it might be a customized subclass.
                        not isinstance(original_widget, ReadOnlyWidget)
                        # And we do not set the widget for subforms, since
                        # they handle readonly by themselves.
                        and not isinstance(base_field, SubformField)
                    )
                    if make_read_only:
                        widget = ReadOnlyWidget(
                            bound_field=field,
                            original_widget=original_widget,
                        )
                        base_field.widget = instance_field.disabled = widget
                    made_readonly = True

                # Readonly fields are disabled automatically.
                if made_readonly or (disabled == all_macro or field_name in disabled):
                    base_field.disabled = instance_field.disabled = True

                if field_name in hidden:
                    base_field.widget = instance_field.widget = HiddenInput()

            result = callback()

        return result
