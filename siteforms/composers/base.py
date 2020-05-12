from collections import defaultdict
from functools import partial
from typing import Dict, Any, Optional, Union, List, Type

from django.forms import BoundField, CheckboxInput, Form
from django.forms.utils import flatatt
from django.forms.widgets import Input
from django.middleware.csrf import get_token
from django.utils.translation import gettext_lazy as _

from ..utils import merge_dict

if False:  # pragma: nocover
    from ..toolbox import SiteformsMixin  # noqa

# todo hidden fields

TypeAttrs = Dict[Union[str, Type[Input]], Any]


ALL_FIELDS = '__fields__'
"""Denotes every field."""

ALL_GROUPS = '__groups__'
"""Denotes every group."""

ALL_ROWS = '__rows__'
"""Denotes every row."""

FORM = '__form__'
"""Denotes a form."""

SUBMIT = '__submit__'
"""Submit button."""

_VALUE = '__value__'


class FormatDict(dict):

    def __missing__(self, key: str) -> str:
        return ''


class FormComposer:
    """Base form composer."""
    
    opt_render_form: bool = True
    """Render form tag."""

    opt_render_labels: bool = True
    """Render label elements."""

    opt_render_help: bool = True
    """Render hints (help texts)."""

    opt_placeholder_label: bool = False
    """Put title (verbose name) into field's placeholders."""

    opt_placeholder_help: bool = False
    """Put hint (help text) into field's placeholders."""

    opt_help_tag: str = 'small'
    """Tag to be used for hints."""

    opt_submit: str = _('Submit')
    """Submit button text."""

    ########################################################

    attrs_labels: TypeAttrs = None
    """Attributes to apply to labels."""

    attrs_help: TypeAttrs = None
    """Attributes to apply to hints."""

    groups: Dict[str, str] = None
    """Map alias to group titles."""

    wrappers: TypeAttrs = {
        ALL_FIELDS: '<span>{field}</span>',
        ALL_ROWS: '<div {attrs}>{fields}</div>',
        ALL_GROUPS: '<fieldset {attrs}><legend>{title}</legend>{rows}</fieldset>',
    }
    """Wrappers for fields and groups."""

    layout: TypeAttrs = {
        FORM: ALL_FIELDS,
        ALL_FIELDS: '{label}{field}{help}',
        CheckboxInput: '{field}{label}{help}',
    }
    """Layout instructions for fields and form."""

    ########################################################

    def __init__(self, form: Union['SiteformsMixin', Form]):
        self.form = form

    def __init_subclass__(cls) -> None:
        # Implements attributes enrichment - inherits attrs values from parents.
        super().__init_subclass__()

        def enrich_attr(attr: str):
            attrs_dict = {}

            for base in cls.__bases__:
                if issubclass(base, FormComposer):
                    attrs_dict = merge_dict(getattr(base, attr), attrs_dict)

            setattr(cls, attr, merge_dict(getattr(cls, attr), attrs_dict))

        enrich_attr('attrs')
        enrich_attr('attrs_labels')
        enrich_attr('attrs_help')
        enrich_attr('wrappers')
        enrich_attr('layout')
        cls._hook_init_subclass()

    @classmethod
    def _hook_init_subclass(cls):
        """"""

    def _get_attr_aria_describedby(self, field: BoundField) -> Optional[str]:
        if self.opt_render_help:
            return f'{field.id_for_label}_help'
        return None

    def _get_attr_aria_label(self, field: BoundField) -> Optional[str]:
        if not self.opt_render_labels:
            return field.label
        return None

    attrs: TypeAttrs = {
        FORM: {
            'method': 'POST',  # todo multipart for files
        },
        ALL_FIELDS: {
            'aria-describedby': _get_attr_aria_describedby,
            'aria-label': _get_attr_aria_label,
        },
    }
    """Attributes to apply to basic elements (form, fields, groups)."""

    def _attrs_get(self, container: Dict[str, Any], key: str = None, *, obj: Any = None):

        if key is None:
            attrs = container
        else:
            attrs = container.get(key, {})

        if attrs:
            if not isinstance(attrs, dict):
                attrs = {_VALUE: attrs}

            attrs_ = {}
            for key, val in attrs.items():

                if callable(val):
                    if obj is None:
                        val = val(self)
                    else:
                        val = val(self, obj)

                if val is not None:
                    attrs_[key] = val

            attrs = attrs_

        return attrs

    def _attrs_get_basic(self, container: Dict[str, Any], field: BoundField):
        get_attrs = partial(self._attrs_get, container, obj=field)

        return {
            **get_attrs(ALL_FIELDS),
            **get_attrs(field.field.widget.__class__),
            **get_attrs(field.name),
        }

    def _render_field(self, field: BoundField, attrs: TypeAttrs = None) -> str:

        attrs = attrs or self._attrs_get_basic(self.attrs, field)

        placeholder = attrs.get('placeholder')

        if placeholder is None:
            if self.opt_placeholder_label:
                attrs['placeholder'] = field.label

            elif self.opt_placeholder_help:
                attrs['placeholder'] = field.help_text

        out = field.as_widget(attrs=attrs)

        if field.field.show_hidden_initial:
            out += field.as_hidden(only_initial=True)

        return f'{out}'

    def _render_label(self, field: BoundField) -> str:
        label = field.label_tag(
            attrs=self._attrs_get_basic(self.attrs_labels, field),
            label_suffix='' if isinstance(field.field.widget, CheckboxInput) else None
        )
        return f'{label}'

    def _render_help(self, field: BoundField) -> str:
        help_text = field.help_text

        if not help_text:
            return ''

        attrs = self._attrs_get_basic(self.attrs_help, field)
        attrs['id'] = f'{field.id_for_label}_help'
        help_tag = self.opt_help_tag

        return f'<{help_tag} {flatatt(attrs)}>{help_text}</{help_tag}>'

    def _render_field_box(self, field: BoundField) -> str:

        layout = self._attrs_get_basic(self.layout, field)

        label = ''
        help = ''

        if self.opt_render_labels:
            label = self._render_label(field)

        if self.opt_render_help:
            help = self._render_help(field)

        out = layout[_VALUE].format_map(FormatDict(
            label=label,
            field=self._render_field(field),
            help=help,
        ))

        wrapper = self._attrs_get_basic(self.wrappers, field)
        out = wrapper[_VALUE].format_map(FormatDict(
            field=out,
        ))

        return out

    def _render_group(self, alias: str, *, rows: List[str]) -> str:
        title = self.groups.get(alias)

        get_attrs = self._attrs_get
        attrs = self.attrs
        wrappers = self.wrappers

        def get_group_params(container: dict) -> dict:
            get_params = partial(get_attrs, container)
            return {**get_params(ALL_GROUPS), **get_params(alias)}

        group_attrs = get_group_params(attrs)
        group_wrapper = get_group_params(wrappers)[_VALUE]

        row_wrapper = get_attrs(wrappers, ALL_ROWS)[_VALUE]

        html = group_wrapper.format_map(FormatDict(
            attrs=flatatt(group_attrs),
            title=title,
            rows='\n'.join(
                row_wrapper.format_map(FormatDict(
                    attrs=flatatt(get_attrs(attrs, ALL_ROWS, obj=fields)),
                    fields='\n'.join(fields),
                ))
                for fields in rows
            )
        ))

        return html

    def _render_layout(self) -> str:
        render_field_box = self._render_field_box
        form = self.form

        # todo
        visible = form.visible_fields()
        hidden = form.hidden_fields()
        multipart = form.is_multipart()

        fields = {name: render_field_box(form[name]) for name in form.fields}

        form_layout = self.layout[FORM]

        out = []

        if isinstance(form_layout, str):
            # Simple layout defined by macros.

            if form_layout == ALL_FIELDS:
                # all fields, no grouping
                out.extend(fields.values())

            else:
                raise ValueError(f'Unsupported form layout macros: {form_layout}')

        elif isinstance(form_layout, dict):
            # Advanced layout with groups.
            render_group = self._render_group
            grouped = defaultdict(list)

            for group_alias, rows in form_layout.items():

                if isinstance(rows, str):
                    # Macros.

                    if rows == ALL_FIELDS:
                        # All the fields left as separate rows.
                        grouped[group_alias].extend([[field] for field in fields.values()])

                    else:
                        raise ValueError(f'Unsupported group layout macros: {rows}')

                else:

                    for row in rows:
                        if isinstance(row, str):
                            # One field in row.
                            grouped[group_alias].append([fields.pop(row)])

                        else:
                            # Several fields in row.
                            row_fields = [fields.pop(group_field) for group_field in row]
                            grouped[group_alias].append(row_fields)

            for group_alias, rows in grouped.items():
                out.append(render_group(group_alias, rows=rows))

        return '\n'.join(out)

    def render(self) -> str:
        """Renders form to string."""

        # todo global errors where to place?
        # errors_global = form.non_field_errors()

        html = self._render_layout()

        if self.opt_render_form:
            get_attr = partial(self._attrs_get, self.attrs)
            request = self.form.request

            csrf = ''
            if request:
                csrf = f'<input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">'

            submit = f'<button type="submit" {flatatt(get_attr(SUBMIT))}>{self.opt_submit}</button>'

            html = f"<form {flatatt(get_attr(FORM))}>{csrf}{html}{submit}</form>"

        return html
