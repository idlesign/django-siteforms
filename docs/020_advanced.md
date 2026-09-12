# Advanced

Composers allow declarative configuration through class attributes, which is enough for many
common cases.

Inherit a nested composer from the required base composer and override the attributes and options
you need.

```python
from siteforms.composers.bootstrap5 import Bootstrap5


class Composer(Bootstrap5):

    opt_render_labels = False
    opt_placeholder_label = True

    attrs_help = {'class': 'some', 'data-one': 'other'}
```

## Attributes

- `attrs` - Attributes to apply to basic elements (form, fields, widget types, groups).
- `attrs_labels` - Attributes to apply to labels.
- `attrs_help` - Attributes to apply to hints.
- `attrs_feedback` - Attributes to apply to feedback (validation notes).
- `wrappers` - Wrappers for fields, groups, rows, submit button.
- `groups` - Map alias to group titles. Groups can be addressed in `layout`.
- `layout` - Layout instructions for fields and form.

## Options

- `opt_form_inline` - Make form inline.
- `opt_render_form_tag` - Render form tag. On by default.
- `opt_label_colon` - Whether to render colons after label's texts.
- `opt_render_labels` - Render label elements.
- `opt_render_help` - Render hints (help texts).
- `opt_placeholder_label` - Put title (verbose name) into field's placeholders.
- `opt_placeholder_help` - Put hint (help text) into field's placeholders.
- `opt_title_label` - Put title (verbose name) into field's title.
- `opt_title_help` - Put hint (help text) into field's title.
- `opt_tag_help` - Tag to be used for hints.
- `opt_tag_feedback` - Tag to be used for feedback.
- `opt_submit` - Submit button text. If not set, submit button won't be added into this form.
- `opt_submit_name` - Submit button name.

## Macros

Macros are a quick way to address various objects.

They can be used as keys in `Attributes` (see above).

- `ALL_FIELDS` - Denotes every field.
- `ALL_GROUPS` - Denotes every group.
- `ALL_ROWS` - Denotes every row.
- `FORM` - Denotes a form.
- `SUBMIT` - Submit button.

## ALL_FIELDS in Layout

The `ALL_FIELDS` macro can be used in many places in a layout. It expands into rows for each field
that has not been addressed yet.

### As layout value

This one is the default.

```python
layout = {
    FORM: ALL_FIELDS
}
```

### As group value

```python
layout = {
    FORM: {
        'basic': [  # group
            ['title', 'date_created'],  # row1
            'contents',  # row2
        ],
        'other': ALL_FIELDS,  # rest rows
    }
}
```

### As group row

```python
layout = {
    FORM: {
        'basic': [  # group
            ['title', 'date_created'],  # row1
            ALL_FIELDS,  # rest rows
        ],
    }
}
```

## Subforms

A subform renders another form in place of a parent form field. Depending on the original field,
`siteforms` can use an inline form for a JSON-encoded value or a foreign key, or a model formset for
a many-to-many relation.

See the [Subforms guide](025_subforms/index.md) for complete JSON, foreign-key, many-to-many, and
nested examples, as well as validation and saving behaviour.

## Multiple forms

Use a unique prefix and the generated submit markers to process multiple forms independently. See
[Multiple forms on one page](015_core_concepts.md#multiple-forms-on-one-page) for a complete
example.
