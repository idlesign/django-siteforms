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

    def __missing__(self, key: str) -> str:  # pragma: nocover
        return ''


class FormComposer:
    """Base form composer."""
    
    opt_render_form: bool = True
    """Render form tag."""

    opt_label_colon: bool = True
    """Whether to render colons after label's texts."""

    opt_render_labels: bool = True
    """Render label elements."""

    opt_render_help: bool = True
    """Render hints (help texts)."""

    opt_placeholder_label: bool = False
    """Put title (verbose name) into field's placeholders."""

    opt_placeholder_help: bool = False
    """Put hint (help text) into field's placeholders."""

    opt_tag_help: str = 'small'
    """Tag to be used for hints."""

    opt_tag_feedback: str = 'span'
    """Tag to be used for feedback."""

    opt_submit: str = _('Submit')
    """Submit button text."""

    opt_submit_name: str = '__submit'
    """Submit button name."""

    ########################################################

    attrs_labels: TypeAttrs = None
    """Attributes to apply to labels."""

    attrs_help: TypeAttrs = None
    """Attributes to apply to hints."""

    attrs_feedback: TypeAttrs = None
    """Attributes to apply to feedback (validation notes)."""

    groups: Dict[str, str] = None
    """Map alias to group titles."""

    wrappers: TypeAttrs = {
        ALL_FIELDS: '<span>{field}</span>',
        ALL_ROWS: '<div {attrs}>{fields}</div>',
        ALL_GROUPS: '<fieldset {attrs}><legend>{title}</legend>{rows}</fieldset>',
        SUBMIT: '{submit}'
    }
    """Wrappers for fields, groups, rows, submit button."""

    layout: TypeAttrs = {
        FORM: ALL_FIELDS,
        ALL_FIELDS: '{label}{field}{feedback}{help}',
        CheckboxInput: '{field}{label}{feedback}{help}',
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

    def _get_attr_form_enctype(self):

        if self.form.is_multipart():
            return 'multipart/form-data'

        return None

    def _get_attr_form_method(self):
        return self.form.src or 'POST'

    attrs: TypeAttrs = {
        FORM: {
            'method': _get_attr_form_method,
            'enctype': _get_attr_form_enctype,
        },
        ALL_FIELDS: {
            'aria-describedby': _get_attr_aria_describedby,
            'aria-label': _get_attr_aria_label,
        },
    }
    """Attributes to apply to basic elements (form, fields, widget types, groups)."""

    def _attrs_get(self, container: Optional[Dict[str, Any]], key: str = None, *, obj: Any = None):

        container = container or {}

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
            label_suffix=(
                # Get rid of colons entirely.
                '' if not self.opt_label_colon else (
                    # Or deduce...
                    '' if isinstance(field.field.widget, CheckboxInput) else None
                )
            )
        )
        return f'{label}'

    def _format_feedback_lines(self, errors: List) -> str:
        return '\n'.join([f'<div>{error}</div>' for error in errors])

    def _render_feedback(self, field: BoundField) -> str:

        if not self.form.is_submitted:
            return ''

        errors = field.errors
        if not errors:
            return ''

        attrs = self._attrs_get_basic(self.attrs_feedback, field)
        tag = self.opt_tag_feedback

        return f'<{tag} {flatatt(attrs)}>{self._format_feedback_lines(errors)}</{tag}>'

    def _render_help(self, field: BoundField) -> str:
        help_text = field.help_text

        if not help_text:
            return ''

        attrs = self._attrs_get_basic(self.attrs_help, field)
        attrs['id'] = f'{field.id_for_label}_help'
        tag = self.opt_tag_help

        return f'<{tag} {flatatt(attrs)}>{help_text}</{tag}>'

    def _format_value(self, src: dict, **kwargs) -> str:
        return src[_VALUE].format_map(FormatDict(**kwargs))

    def _apply_layout(self, *, fld: BoundField, field: str, label: str, hint: str, feedback: str) -> str:
        return self._format_value(
            self._attrs_get_basic(self.layout, fld),
            label=label,
            field=field,
            help=hint,
            feedback=feedback,
        )

    def _apply_wrapper(self, *, fld: BoundField, content) -> str:
        return self._format_value(
            self._attrs_get_basic(self.wrappers, fld),
            field=content,
        )

    def _render_field_box(self, field: BoundField) -> str:

        if field.is_hidden:
            return str(field)

        label = ''
        hint = ''

        if self.opt_render_labels:
            label = self._render_label(field)

        if self.opt_render_help:
            hint = self._render_help(field)

        out = self._apply_layout(
            fld=field,
            field=self._render_field(field),
            label=label,
            hint=hint,
            feedback=self._render_feedback(field),
        )

        return self._apply_wrapper(fld=field, content=out)

    def _render_group(self, alias: str, *, rows: List[str]) -> str:
        title = self.groups.get(alias)

        get_attrs = self._attrs_get
        attrs = self.attrs
        wrappers = self.wrappers
        format_value = self._format_value

        def get_group_params(container: dict) -> dict:
            get_params = partial(get_attrs, container)
            return {**get_params(ALL_GROUPS), **get_params(alias)}

        group_attrs = get_group_params(attrs)

        html = format_value(
            get_group_params(wrappers),
            attrs=flatatt(group_attrs),
            title=title,
            rows='\n'.join(
                format_value(
                    get_attrs(wrappers, ALL_ROWS),
                    attrs=flatatt(get_attrs(attrs, ALL_ROWS, obj=fields)),
                    fields='\n'.join(fields),
                )
                for fields in rows
            )
        )

        return html

    def _render_layout(self) -> str:
        render_field_box = self._render_field_box
        form = self.form

        fields = {name: render_field_box(form[name]) for name in form.fields}

        form_layout = self.layout[FORM]

        out = []

        if isinstance(form_layout, str):
            # Simple layout defined by macros.

            if form_layout == ALL_FIELDS:
                # all fields, no grouping
                out.extend(fields.values())

            else:  # pragma: nocover
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

                    else:  # pragma: nocover
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

    def _render_submit(self) -> str:
        get_attr = self._attrs_get
        return self._format_value(
            get_attr(self.wrappers, SUBMIT),
            submit=f'<button type="submit" name="{self.opt_submit_name}" {flatatt(get_attr(self.attrs, SUBMIT))}>{self.opt_submit}</button>'
        )

    def render(self) -> str:
        """Renders form to string."""

        # todo global errors where to place?
        # errors_global = self.form.non_field_errors()

        html = self._render_layout()

        if self.opt_render_form:
            get_attr = partial(self._attrs_get, self.attrs)
            request = self.form.request

            csrf = ''
            if request:
                csrf = f'<input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">'

            html = (
                f"<form {flatatt(get_attr(FORM))}>"
                f"{csrf}"
                f"{html}"
                f"{self._render_submit()}"
                "</form>"
            )

        return html
