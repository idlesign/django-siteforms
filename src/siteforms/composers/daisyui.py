from django.forms import (
    BoundField, CheckboxInput, CheckboxSelectMultiple, ClearableFileInput, FileInput, RadioSelect, Select, SelectMultiple,
    Textarea,
)

from .base import FormComposer, TypeAttrs, ALL_FIELDS, ALL_GROUPS, FORM, SUBMIT, FIELDS_READONLY


class Daisyui(FormComposer):
    """DaisyUI 5 theming composer.

    Targets DaisyUI component classes on top of Tailwind CSS 4.
    No JavaScript is required for the generated markup.

    """

    SIZE_SMALL = 'sm'
    SIZE_NORMAL = ''
    SIZE_LARGE = 'lg'

    opt_size: str = SIZE_NORMAL
    """Apply size to form elements."""

    opt_checkbox_toggle: bool = False
    """Use toggles instead of checkboxes."""

    opt_feedback_valid: bool = False
    """Whether to highlight valid fields after form submission."""

    opt_tag_help: str = 'p'

    def _get_attr_submit(self) -> str:
        css = 'btn btn-primary mt-4'

        if self.opt_size:
            css = f'{css} btn-{self.opt_size}'

        return css

    def _get_attr_checkbox(self, field: BoundField) -> str:

        if self.opt_checkbox_toggle:
            return 'toggle'

        return 'checkbox'

    def _render_field(self, field: BoundField, attrs: TypeAttrs = None) -> str:
        attrs = attrs or self._attrs_get_basic(self.attrs, field)

        css = attrs.get('class', '')
        base_css = css.split(' ')[0]

        if base_css:

            if self.opt_size:
                css = f'{css} {base_css}-{self.opt_size}'

            if self.form.is_submitted:

                if field.errors:
                    css = f'{css} {base_css}-error'

                elif self.opt_feedback_valid:
                    css = f'{css} {base_css}-success'

        attrs['class'] = css

        return super()._render_field(field, attrs)

    attrs: TypeAttrs = {
        SUBMIT: {'class': _get_attr_submit},
        ALL_FIELDS: {'class': 'input'},
        ALL_GROUPS: {'class': 'fieldset bg-base-200 border border-base-300 rounded-box p-4 mb-4'},
        FIELDS_READONLY: {'class': 'input bg-base-200'},
        CheckboxInput: {'class': _get_attr_checkbox},
        CheckboxSelectMultiple: {'class': 'checkbox'},
        RadioSelect: {'class': 'radio'},
        Select: {'class': 'select'},
        SelectMultiple: {'class': 'select'},
        Textarea: {'class': 'textarea'},
        FileInput: {'class': 'file-input'},
        ClearableFileInput: {'class': 'file-input'},
    }

    attrs_help: TypeAttrs = {
        ALL_FIELDS: {'class': 'label'},
    }

    attrs_feedback: TypeAttrs = {
        FORM: {'class': 'alert alert-error mb-4', 'role': 'alert'},
        ALL_FIELDS: {'class': 'text-error mt-1'},
    }

    attrs_labels: TypeAttrs = {
        ALL_FIELDS: {'class': 'label'},
    }

    wrappers: TypeAttrs = {
        ALL_FIELDS: '<fieldset class="fieldset">{field}</fieldset>',
        ALL_GROUPS: '<fieldset {attrs}><legend class="fieldset-legend">{title}</legend>{rows}</fieldset>',
    }
