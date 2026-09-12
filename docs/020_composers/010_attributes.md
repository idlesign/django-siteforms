# Element attributes

Composer attribute mappings add or change HTML attributes without replacing widgets or templates.
The main mappings are:

| Mapping | Target element |
|---|---|
| `attrs` | Form, submit button, groups, rows, and field widgets |
| `attrs_labels` | Field labels |
| `attrs_help` | Field help text |
| `attrs_feedback` | Field validation feedback and non-field errors |

## Targeting fields

Use `ALL_FIELDS`, an exact widget class, or a field name as a key. Rules are applied in that order,
so the more specific rule can override the earlier one:

```python
from django.forms import Textarea

from siteforms.composers.bootstrap5 import Bootstrap5
from siteforms.composers.base import ALL_FIELDS


class Composer(Bootstrap5):
    attrs = {
        ALL_FIELDS: {
            'data-form-control': 'true',
        },
        Textarea: {
            'rows': 4,
        },
        'summary': {
            'rows': 2,
            'autocomplete': 'off',
        },
    }
```

This applies `data-form-control` to every field, `rows="4"` to textareas, and then overrides rows
for the field named `summary`.

Widget matching uses the widget's exact class. Target a custom widget class explicitly when its
attributes must differ from those of its base widget.

## Appending attribute values

Prefix a value with `+` to append it to a value accumulated from a broader field rule. This is
particularly useful for CSS classes supplied by Bootstrap composers:

```python
from siteforms.composers.bootstrap5 import Bootstrap5


class Composer(Bootstrap5):
    attrs = {
        'email': {
            'class': '+border-warning',
        },
    }
```

The `email` control retains its `form-control` class and also receives `border-warning`. Without
the `+`, the field-specific value replaces the accumulated class value.

Appending is available while resolving field rules. Form, group, row, and submit-button mappings
do not accumulate the same way; specify their complete value or use a callable.

## Forms, groups, rows, and submit buttons

Use composer macros to target structural elements:

```python
from siteforms.composers.base import ALL_GROUPS, ALL_ROWS, FORM, SUBMIT
from siteforms.composers.bootstrap5 import Bootstrap5


class Composer(Bootstrap5):
    attrs = {
        FORM: {
            'class': 'article-form',
            'novalidate': True,
        },
        ALL_GROUPS: {
            'class': 'border rounded p-3',
        },
        ALL_ROWS: {
            'data-layout': 'row',
        },
        SUBMIT: {
            'class': 'btn btn-success',
        },
    }
```

A group alias can replace `ALL_GROUPS` to target one named group:

```python
attrs = {
    'publication': {
        'class': 'border-warning',
    },
}
```

Whether a key identifies a field or a group depends on where it is used by the current layout.
Avoid giving a field and a group the same name.

## Labels, help, and feedback

These mappings use the same field targeting rules:

```python
from siteforms.composers.base import ALL_FIELDS, FORM
from siteforms.composers.bootstrap5 import Bootstrap5


class Composer(Bootstrap5):
    attrs_labels = {
        'email': {
            'class': '+fw-bold',
        },
    }
    attrs_help = {
        ALL_FIELDS: {
            'data-role': 'field-help',
        },
    }
    attrs_feedback = {
        FORM: {
            'class': 'alert alert-danger',
            'role': 'alert',
        },
        ALL_FIELDS: {
            'data-role': 'field-error',
        },
    }
```

`FORM` inside `attrs_feedback` targets non-field errors, not the `<form>` element. Use `FORM`
inside `attrs` for the element itself.

## Dynamic values

An attribute value may be callable. A field attribute callable receives the composer and the
bound field:

```python
def field_state(composer, field):
    return 'required' if field.field.required else 'optional'


class Composer(Bootstrap5):
    attrs = {
        ALL_FIELDS: {
            'data-state': field_state,
        },
    }
```

Form, group, and submit-button callables receive the composer. Row callables receive the composer
and the current field mapping. Each callable can inspect `composer.form` to derive a value from the
current form instance.
