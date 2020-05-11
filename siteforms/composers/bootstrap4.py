from typing import Optional, Tuple, List

from django.forms import FileInput, ClearableFileInput, CheckboxInput, BoundField, Select, SelectMultiple

from .base import FormComposer, TypeAttrs, ALL_FIELDS, FORM, ALL_GROUPS, ALL_ROWS, SUBMIT  # noqa


class Bootstrap4(FormComposer):
    """Bootstrap 4 theming composer."""

    SIZE_SMALL = 'sm'
    SIZE_NORMAL = ''
    SIZE_LARGE = 'lg'

    opt_form_inline: bool = False
    """Make fields inline."""

    opt_size: str = SIZE_NORMAL
    """Apply size to form elements."""

    opt_help_tag: str = 'small'
    """Tag to be used for hints."""

    opt_disabled_plaintext: bool = True
    """Render disabled fields as plain text."""

    _size_mod: Tuple[str, ...] = ('col-form-label', 'form-control', 'input-group')
    _file_cls = {'class': 'form-control-file'}

    def _get_attr_form(self) -> Optional[str]:
        # todo maybe needs-validation and novalidate
        if self.opt_form_inline:
            return 'form-inline'
        return None

    def _get_attr_check_input(self, field: BoundField):
        css = 'form-check-input'
        if not self.opt_render_labels:
            css += ' position-static'
        return css

    def _get_attr_rows(self, fields: List[str]) -> Optional[str]:
        if len(fields) > 1:
            return 'form-row mx-0'
        return None

    def _render_field(self, field: BoundField, attrs: TypeAttrs = None) -> str:
        attrs = attrs or self._attrs_get_basic(self.attrs, field)

        css = attrs.get('class', '')

        if self.form.data:
            # Only if data submitted.

            if field.errors:
                css += ' is-invalid'
            else:
                css += ' is-valid'

        if self.opt_disabled_plaintext:
            is_disabled = field.name in self.form.disabled_fields
            if is_disabled:
                css = ' form-control-plaintext'

        attrs['class'] = css

        return super()._render_field(field, attrs)

    def render(self) -> str:
        out = super().render()

        size = self.opt_size

        if size:
            # Apply sizing.
            mod = f'-{size}'

            # Workaround form-control- prefix clashes.
            clashing = {}
            for idx, term in enumerate(('form-control-file', 'form-control-plaintext')):
                tmp_key = f'tmp_{idx}'
                clashing[tmp_key] = term
                out = out.replace(term, tmp_key)

            for val in self._size_mod:
                out = out.replace(val, f'{val} {val}{mod}')

            # Roll off the workaround.
            for tmp_key, term in clashing.items():
                out = out.replace(tmp_key, term)

        return out

    attrs: TypeAttrs = {
        FORM: {'class': _get_attr_form, 'novalidate': ''},
        SUBMIT: {'class': 'btn btn-primary mt-3'},  # todo control-group?
        ALL_FIELDS: {'class': 'form-control'},
        ALL_ROWS: {'class': _get_attr_rows},
        ALL_GROUPS: {'class': 'form-group'},
        FileInput: _file_cls,
        ClearableFileInput: _file_cls,
        CheckboxInput: {'class': _get_attr_check_input},
    }

    attrs_help: TypeAttrs = {
        ALL_FIELDS: {'class': 'form-text text-muted'},
    }

    attrs_labels: TypeAttrs = {
        CheckboxInput: {'class': 'form-check-label'},
    }

    wrappers: TypeAttrs = {
        # todo invalida feedback
        # <div class="valid-feedback">Looks good!</div><div class="invalid-feedback">Please choose a username.</div>
        ALL_FIELDS: '<div class="form-group mx-1">{field}</div>',
        CheckboxInput: '<div class="form-group form-check">{field}</div>',  # todo +form-check-inline
    }


class Bootstrap4Columns(Bootstrap4):
    """Mixin that allows two-columns form layout: labels column + controls column."""

    opt_columns: Tuple[str, str] = ('col-2', 'col-10')
    """Columns tuple: (label_columns_count, control_columns_count)."""

    _wrapper = '<div class="form-group row">{field}</div>'

    def _get_layout_columns(self, field: BoundField) -> str:
        label, control = self.opt_columns
        if isinstance(field.field.widget, CheckboxInput):
            return f'<div class="{label}"></div><div class="{control}">{{field}}{{label}}{{help}}</div>'
        return f'<div class="{label}">{{label}}</div><div class="{control}">{{field}}{{help}}</div>'

    attrs_labels: TypeAttrs = {
        ALL_FIELDS: {'class': 'col-form-label'},
    }

    wrappers = {
        ALL_ROWS: '{fields}',
        ALL_FIELDS: _wrapper,
        CheckboxInput: _wrapper,
    }

    layout = {
        ALL_FIELDS: _get_layout_columns,
        CheckboxInput: _get_layout_columns,
    }


class Bootstrap4Custom(Bootstrap4):
    """Bootstrap 4 theming composer with some custom elements."""

    opt_checkbox_switch: bool = True
    """Use switches for checkboxes."""

    _size_mod: Tuple[str, ...] = tuple(list(Bootstrap4._size_mod) + [
        'custom-select',
    ])

    _file_cls = {'class': 'custom-file-input'}
    _file_label = {'class': 'custom-file-label'}
    _file_wrapper = '<div class="custom-file mx-1">{field}</div>'
    _select_cls = {'class': 'custom-select'}

    def _get_wrapper_checkbox(self, field: BoundField) -> Optional[str]:
        variant = "custom-switch" if self.opt_checkbox_switch else "custom-checkbox"
        # todo +custom-control-inline
        return f'<div class="custom-control mx-1 {variant}">{{field}}</div>'

    attrs: TypeAttrs = {
        FileInput: _file_cls,
        ClearableFileInput: _file_cls,
        Select: _select_cls,
        SelectMultiple: _select_cls,
        CheckboxInput: {'class': 'custom-control-input'},
    }

    attrs_labels: TypeAttrs = {
        FileInput: _file_label,
        ClearableFileInput: _file_label,
        CheckboxInput: {'class': 'custom-control-label'},
    }

    wrappers: TypeAttrs = {
        FileInput: _file_wrapper,
        ClearableFileInput: _file_wrapper,
        CheckboxInput: _get_wrapper_checkbox,
    }
