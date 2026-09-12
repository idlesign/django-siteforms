# Bootstrap 4

Use `Bootstrap4` in applications that load Bootstrap 4 assets:

```python
from siteforms.composers.bootstrap4 import Bootstrap4
from siteforms.toolbox import Form, fields


class ContactForm(Form):
    email = fields.EmailField()
    message = fields.CharField(widget=fields.Textarea)

    class Composer(Bootstrap4):
        opt_submit = 'Send'
```

Bootstrap 4 and Bootstrap 5 use different form-control and validation structures. Select this
composer based on the loaded CSS major version rather than mixing composer features between them.

## Inline forms

```python
class Composer(Bootstrap4):
    opt_form_inline = True
```

This adds Bootstrap 4's `form-inline` class. Use ordinary composer `attrs` to add any application
specific classes or data attributes.

## Label and control columns

Use the default `('col-2', 'col-10')` pair or provide explicit Bootstrap classes:

```python
class Composer(Bootstrap4):
    opt_columns = ('col-sm-4', 'col-sm-8')
```

Column mode creates Bootstrap 4 form rows and places labels and controls into the corresponding
columns.

## Native and custom controls

Bootstrap 4 supports its custom form-control family. Enable it at composer declaration time:

```python
class Composer(Bootstrap4):
    opt_custom_controls = True
```

This changes classes and wrappers for selects, file inputs, and checkboxes. With custom controls
enabled, Boolean fields can be rendered as switches:

```python
class Composer(Bootstrap4):
    opt_custom_controls = True
    opt_checkbox_switch = True
```

`opt_checkbox_switch` depends on `opt_custom_controls` in Bootstrap 4. These options modify composer
mappings when the class is created, so declare them on the class rather than changing an instance.

## Sizes

```python
class SmallComposer(Bootstrap4):
    opt_size = Bootstrap4.SIZE_SMALL


class LargeComposer(Bootstrap4):
    opt_size = Bootstrap4.SIZE_LARGE
```

`SIZE_NORMAL` is the default. Size classes are applied to the Bootstrap elements that support
small or large variants.

## Disabled plaintext

```python
class Composer(Bootstrap4):
    opt_disabled_plaintext = True
```

Fields explicitly listed in `disabled_fields` use Bootstrap 4's plaintext styling. Use siteforms
read-only rendering instead when the whole form is a detail view.

## Validation feedback

Submitted controls receive `is-invalid` when they contain errors. Valid controls receive
`is-valid` unless positive feedback is disabled:

```python
class Composer(Bootstrap4):
    opt_feedback_valid = False
```

Use Bootstrap 4 tooltip feedback instead of ordinary feedback blocks with:

```python
class Composer(Bootstrap4):
    opt_feedback_tooltips = True
```

Hidden helper controls are added where Bootstrap requires a control carrying `is-invalid` for
nested feedback to become visible.

## Moving from Bootstrap 4 to 5

When the application upgrades its assets:

1. change the composer base to `Bootstrap5`;
2. remove `opt_custom_controls`, which has no Bootstrap 5 equivalent;
3. review inline, spacing, file-input, select, and checkbox output;
4. test column layouts and validation feedback in the browser;
5. replace Bootstrap 4-specific classes in custom `attrs` and `wrappers`.

The form, field-state, filtering, and subform APIs do not change when only the composer base is
replaced.

See the [Composer API](../020_composers/050_api.md) for defaults generated through `apidescribed`.
