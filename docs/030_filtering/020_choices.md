# Optional fields and undefined choices

Filtering forms modify field requirements and choices so that leaving a control empty means "do
not add a lookup".

## Optional fields

`filtering_fields_optional` defaults to `__all__`, making every generated and declared form field
optional for filtering:

```python
class ArticleFilterForm(FilteringModelForm):
    filtering_fields_optional = '__all__'
```

Limit this behaviour to selected fields with a set:

```python
filtering_fields_optional = {
    'title',
    'status',
}
```

Set it to `None` or an empty set to preserve the original `required` state for every field. An
empty required field then makes the filter form invalid, and `filtering_apply()` returns the
original queryset with `applied=False`.

## Undefined choice

`filtering_fields_choice_undefined` defaults to `__all__`. Every field with choices receives an
additional initial option:

```text
----
```

Its default submitted value is `*`. Before validation, the marker is removed so the field is
treated as empty and no queryset lookup is produced.

Limit the extra option to selected fields:

```python
filtering_fields_choice_undefined = {
    'status',
}
```

Or disable it for all fields:

```python
filtering_fields_choice_undefined = None
```

Customize the title and reserved value together when required:

```python
filtering_choice_undefined_title = 'Any status'
filtering_choice_undefined_value = '__any__'
```

The undefined value is reserved across the entire filtering form and is removed from submitted
values before fields are cleaned. Change it if `*` is a legitimate text or choice value in the
filter interface.

For a multiple-choice field, the undefined marker is removed while any other selected values are
preserved.

## Boolean fields

A checkbox does not provide a third "not specified" state: an unchecked Django `BooleanField`
cleans to `False`, which is a non-empty value and therefore applies a `False` filter. Use an
explicit choice field when users must select between any, yes, and no:

```python
enabled = fields.TypedChoiceField(
    choices=[
        ('1', 'Yes'),
        ('0', 'No'),
    ],
    coerce=lambda value: value == '1',
    empty_value=None,
)

filtering_choice_undefined_title = 'Any'
```

The automatically added undefined choice is removed before cleaning, becomes `None`, and is skipped
by `filtering_apply()`.
