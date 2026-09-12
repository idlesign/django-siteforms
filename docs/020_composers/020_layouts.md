# Layouts and wrappers

The `layout` mapping controls which fields are rendered, their order, and how their labels, widgets,
feedback, and help text are combined. The `wrappers` mapping supplies the surrounding HTML.

## Default layout

The default form layout renders every field in declaration order:

```python
from siteforms.composers.base import ALL_FIELDS, FORM


layout = {
    FORM: ALL_FIELDS,
}
```

`ALL_FIELDS` expands to every field that has not already been placed.

## Groups and rows

Set `layout[FORM]` to a mapping to create grouped layouts. Group aliases are mapped to visible
titles through `groups`:

```python
from siteforms.composers.base import ALL_FIELDS, FORM
from siteforms.composers.bootstrap5 import Bootstrap5


class Composer(Bootstrap5):
    groups = {
        'article': 'Article',
        'publication': 'Publication',
    }
    layout = {
        FORM: {
            'article': [
                'title',
                'contents',
            ],
            'publication': [
                ['status', 'published_at'],
            ],
            'other': ALL_FIELDS,
        },
    }
```

In this structure:

- a string such as `'title'` creates a row containing one field;
- a list such as `['status', 'published_at']` places fields in the same row;
- a group value of `ALL_FIELDS` adds all fields not placed earlier, each in its own row.

A layout alias omitted from `groups` still renders as a group, but has an empty title. This is
useful for structural grouping without a legend.

!!! warning
    Once `layout[FORM]` is an explicit group mapping, unreferenced visible fields are omitted.
    Include `ALL_FIELDS` where the remaining fields should appear. Hidden fields are preserved so
    that model formsets can still submit object identifiers.

## Stacked fields

Nest a list inside a row to stack those fields within one row cell:

```python
layout = {
    FORM: {
        'article': [
            [
                'title',
                ['created_at', 'updated_at'],
            ],
            'contents',
        ],
    },
}
```

Here `title` occupies the first part of the row, while `created_at` and `updated_at` are stacked in
the second part. The `FIELDS_STACKED` wrapper controls the markup around the stacked fields.

## Field content order

Besides defining the form structure, `layout` can target fields using `ALL_FIELDS`, widget classes,
and field names. The value is a format string containing any of these placeholders:

- `{label}`;
- `{field}`;
- `{feedback}`;
- `{help}`.

For example, this places help before validation feedback for all fields and puts the control before
the label for one field:

```python
from siteforms.composers.base import ALL_FIELDS
from siteforms.composers.bootstrap5 import Bootstrap5


class Composer(Bootstrap5):
    layout = {
        ALL_FIELDS: '{label}{field}{help}{feedback}',
        'accept_terms': '{field}{label}{feedback}{help}',
    }
```

## Wrapper templates

`wrappers` provides format strings around rendered elements. Available placeholders depend on the
target:

| Target | Placeholders |
|---|---|
| Field or `ALL_FIELDS` | `{field}` |
| `ALL_ROWS` | `{attrs}`, `{fields}` |
| Group or `ALL_GROUPS` | `{attrs}`, `{title}`, `{rows}` |
| `FIELDS_STACKED` | `{field}` |
| `SUBMIT` | `{submit}` |

Example:

```python
from siteforms.composers.base import ALL_GROUPS, ALL_ROWS, SUBMIT
from siteforms.composers.bootstrap5 import Bootstrap5


class Composer(Bootstrap5):
    wrappers = {
        ALL_ROWS: '<section {attrs}>{fields}</section>',
        ALL_GROUPS: '<fieldset {attrs}><legend>{title}</legend>{rows}</fieldset>',
        SUBMIT: '<footer class="form-actions">{submit}</footer>',
    }
```

Composer subclasses automatically enrich inherited `attrs`, `attrs_labels`, `attrs_help`,
`wrappers`, and `layout` mappings. Define only the keys that differ from the parent composer.
