# Bootstrap 5

Inherit the nested composer from `Bootstrap5`:

```python
from siteforms.composers.bootstrap5 import Bootstrap5
from siteforms.toolbox import Form, fields


class ContactForm(Form):
    email = fields.EmailField()
    message = fields.CharField(widget=fields.Textarea)

    class Composer(Bootstrap5):
        opt_submit = 'Send'
```

The application must load Bootstrap 5 CSS. JavaScript is needed only for Bootstrap components used
by the surrounding application; regular form controls and validation classes do not require
siteforms-specific JavaScript.

## Inline forms

`opt_form_inline` applies Bootstrap's responsive row classes to the form:

```python
class Composer(Bootstrap5):
    opt_form_inline = True
    opt_submit = 'Search'
```

Additional form attributes remain available through `attrs`:

```python
from siteforms.composers.base import FORM


class Composer(Bootstrap5):
    opt_form_inline = True
    attrs = {
        FORM: {
            'data-role': 'search-form',
        },
    }
```

## Label and control columns

Enable the default `('col-2', 'col-10')` layout with `True`, or provide a pair of Bootstrap column
classes:

```python
class Composer(Bootstrap5):
    opt_columns = ('col-md-3', 'col-md-9')
```

The first value is used for the label and the second for its control, help text, and validation
feedback. Column mode also adjusts checkbox layout.

Declare column and inline options on the composer class. They alter inherited layout and wrapper
mappings when the class is created and are not intended to be toggled on an already instantiated
composer.

## Floating labels

Enable floating labels and ensure text controls have placeholders:

```python
class Composer(Bootstrap5):
    opt_labels_floating = True
    opt_placeholder_label = True
```

The composer places labels after controls and adds Bootstrap's `form-floating` wrapper. Subform
fields and checkbox controls retain their specialized layouts.

Bootstrap floating-label constraints still apply. In particular, text inputs need a placeholder,
and some control types are not supported by Bootstrap. Use a normal layout for incompatible
widgets.

## Sizes

Use the supplied constants:

```python
class SmallComposer(Bootstrap5):
    opt_size = Bootstrap5.SIZE_SMALL


class LargeComposer(Bootstrap5):
    opt_size = Bootstrap5.SIZE_LARGE
```

The size is applied to labels, controls, selects, and the generated button where Bootstrap has a
corresponding size class. `SIZE_NORMAL` is the default.

## Checkboxes and switches

Regular Boolean fields use Bootstrap's `form-check` markup. Render them as switches with:

```python
class Composer(Bootstrap5):
    opt_checkbox_switch = True
```

This changes presentation only; submitted and cleaned values follow Django's Boolean field rules.

## Disabled plaintext

Explicitly disabled fields normally remain disabled controls. Set `opt_disabled_plaintext` to use
Bootstrap's plaintext class instead:

```python
class ArticleForm(ModelForm):
    disabled_fields = {'slug'}

    class Composer(Bootstrap5):
        opt_disabled_plaintext = True
```

This option applies presentation to fields listed in `disabled_fields`. For display-only pages,
prefer `readonly_fields` and `render_form_tag=False`; see
[Field states and read-only views](../035_field_states.md).

## Validation feedback

After the form is submitted, invalid controls receive `is-invalid` and their errors use
`invalid-feedback`. Valid controls receive `is-valid` by default.

Disable positive feedback or use tooltip markup as follows:

```python
class Composer(Bootstrap5):
    opt_feedback_valid = False
    opt_feedback_tooltips = True
```

Non-field errors use an alert with `role="alert"`. Field help remains connected through
`aria-describedby`, and hiding labels produces `aria-label` values.

See the [Composer API](../020_composers/050_api.md) for defaults generated through `apidescribed`.
