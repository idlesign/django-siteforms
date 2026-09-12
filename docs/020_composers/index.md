# Composers

A composer turns a bound Django form into complete HTML. It controls layout, element attributes,
wrappers, labels, help text, validation feedback, and the submit button without requiring a
form-specific template.

Declare the composer as a nested class on a siteforms form:

```python
from siteforms.composers.bootstrap5 import Bootstrap5
from siteforms.toolbox import Form, fields


class SearchForm(Form):
    query = fields.CharField(label='Search')

    class Composer(Bootstrap5):
        opt_form_inline = True
        opt_submit = 'Search'
```

Choose a base composer according to the desired output:

- `FormComposer` from `siteforms.composers.base` for markup without a CSS framework;
- `Bootstrap5` for Bootstrap 5;
- `Bootstrap4` for Bootstrap 4.

The CSS frameworks themselves are not bundled. Applications must load the corresponding assets.

## Configuration layers

Composer settings fall into three groups:

- **attributes** apply HTML attributes to forms, controls, labels, help text, and feedback;
- **layout and wrappers** define element order and surrounding markup;
- **options** enable common rendering behaviours.

The following guides describe each layer:

- [Element attributes](010_attributes.md)
- [Layouts and wrappers](020_layouts.md)
- [Rendering options](030_options.md)
- [Reusable and custom composers](040_custom.md)
- [Composer API](050_api.md)

For request binding, form tags, and submission detection, see
[Core concepts](../015_core_concepts.md). For composers used by nested forms, see
[Subforms](../025_subforms/index.md).
