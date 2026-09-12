# Subforms

A subform represents a parent form field with another form instead of a single widget. This is
useful for structured JSON-encoded values and for editing related model objects together with the
parent object.

Register subforms by mapping parent field names to form classes:

```python
class ProfileForm(ModelForm):
    subforms = {
        'preferences': PreferencesForm,
        'address': AddressForm,
        'skills': SkillForm,
    }
```

The type of the original parent field determines the integration mode:

| Parent field | Subform representation |
|---|---|
| Regular field containing JSON text | One inline form |
| `ForeignKey` | One inline model form |
| `ManyToManyField` | Model formset |

The parent field must be included in `Meta.fields`. The subform's field names receive the parent
field name as a prefix, such as `address-city` or `skills-0-name`. Nested subforms extend that
prefix further.

Subforms are rendered inside the parent form and do not create their own `<form>` elements or
submit buttons. They receive the parent request, data source, files, and submit marker
automatically.

## Guides

- [JSON-encoded values](010_json.md)
- [Foreign keys](020_foreign_keys.md)
- [Many-to-many relations](030_many_to_many.md)
- [Nested subforms](040_nested.md)
- [Validation, saving, and runtime access](050_lifecycle.md)

!!! note
    Subforms are not a replacement for every Django inline formset use case. They are intended for
    fields that belong to the parent form and whose related values should be validated and saved as
    part of the same form workflow.
