# django-siteforms

*Build complete Django forms without maintaining repetitive form templates.*

django-siteforms renders the form wrapper, CSRF token, fields, validation feedback, and submit
controls. Its composers provide declarative layouts and attributes for plain HTML, Bootstrap 4,
and Bootstrap 5. The same form classes can also model nested relations, read-only detail views,
and queryset filters.

## Start here

Install the package:

```shell
$ python -m pip install django-siteforms
```

Follow the [Quickstart](010_quickstart.md) to build and process a Bootstrap 5 model form. Read
[Core concepts](015_core_concepts.md) next for request binding, submission markers, multiple forms,
and rendering options.

## I want to...

- **Control markup and layout:** see [Composers](020_composers/index.md).
- **Use Bootstrap:** choose the [Bootstrap 5 or Bootstrap 4 guide](040_bootstrap/index.md).
- **Edit JSON or related models:** start with [Subforms](025_subforms/index.md).
- **Filter a queryset with a form:** read [Filtering forms](030_filtering/index.md).
- **Hide, disable, or display fields:** see
  [Field states and read-only views](035_field_states.md).
- **Combine features in a view:** copy a pattern from [Recipes](050_recipes/index.md).
- **Look up a class or option:** use the generated [API reference](090_api/index.md).
- **Diagnose unexpected behavior:** check [Troubleshooting](050_recipes/050_troubleshooting.md).

## Features

- Complete form rendering, including prolog and submit button
- Declarative field groups, layouts, and HTML attributes
- JSON, foreign-key, and many-to-many subforms
- Hidden, disabled, and read-only field states
- Model property fields and multi-value widgets
- Accessible markup
- Queryset filtering forms
- Plain HTML, Bootstrap 4, and Bootstrap 5 composers

## Compatibility

The following combinations are exercised by the GitHub Actions test matrix:

| Python | Django 3.2 | Django 4.2 | Django 5.2 | Django 6.1 |
|---|:---:|:---:|:---:|:---:|
| 3.10 | ✓ | ✓ | ✓ | — |
| 3.11 | — | ✓ | ✓ | — |
| 3.12 | — | ✓ | ✓ | ✓ |
| 3.13 | — | — | ✓ | ✓ |
| 3.14 | — | — | ✓ | ✓ |

The package metadata requires Python 3.10 or newer. Install a Django version compatible with your
Python version; the table lists the combinations continuously verified by this project.

Source code and issue tracking are available on
[GitHub](https://github.com/idlesign/django-siteforms).
