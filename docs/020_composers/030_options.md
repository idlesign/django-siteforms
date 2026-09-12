# Rendering options

Options are composer class attributes whose names start with `opt_`. They cover common rendering
changes that would otherwise require several attribute or layout overrides.

## Labels, help, and field metadata

```python
from siteforms.composers.bootstrap5 import Bootstrap5


class Composer(Bootstrap5):
    opt_label_colon = False
    opt_render_help = False
    opt_placeholder_label = True
    opt_title_help = True
```

Common options include:

- `opt_render_labels` and `opt_render_help` to show or hide labels and help text;
- `opt_label_colon` to control Django's label suffix;
- `opt_placeholder_label` and `opt_placeholder_help` to derive placeholders;
- `opt_title_label` and `opt_title_help` to derive `title` attributes;
- `opt_tag_help`, `opt_tag_feedback`, and `opt_tag_feedback_line` to select output tags.

An explicit `placeholder` or `title` in `attrs` takes precedence over the corresponding derived
value. When labels are hidden, the base composer adds an `aria-label`. When help text is rendered,
it links the control to the help element using `aria-describedby`.

## Form and submit button

```python
class Composer(Bootstrap5):
    opt_render_form_tag = True
    opt_submit = 'Publish'
    opt_submit_name = '__submit'
```

`opt_render_form_tag` controls the generated form wrapper. Disabling it also removes the automatic
CSRF token and submit button; see [Form tag, CSRF, and file uploads](../015_core_concepts.md#form-tag-csrf-and-file-uploads).

`opt_submit` sets the button text. `opt_submit_name` sets the parameter used for submission
detection. If the name is changed, custom templates and application code must submit that same
parameter.

## Bootstrap options

Bootstrap composers add options for:

- inline forms;
- label/control columns;
- small and large control sizes;
- rendering disabled values as plaintext;
- validation tooltips and valid-field feedback;
- checkbox switches;
- Bootstrap 5 floating labels;
- Bootstrap 4 custom controls.

See [Bootstrap 5](../050_bs5.md) and [Bootstrap 4](../040_bs4.md) for the options supported by
each composer. The [Composer API](050_api.md) contains the definitions and defaults sourced from
the implementation through `apidescribed`.
