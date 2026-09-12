# django-siteforms documentation

<https://github.com/idlesign/django-siteforms>

## Description

*Django reusable app to simplify form construction*

For those who consider maintaining templates-based forms solutions for Django a burden.

Features:

- Full form rendering support, including prolog and submit button
- Subforms support (represent entire other form as a form field): JSON, Foreign Key, Many-to-Many
- Field groups
- Declarative attributes for elements
- Simplified declarative forms layout, allowing fields ordering
- Simple ways to make fields hidden, disabled, readonly
- Support for fields from model's properties
- Aria-friendly (Accessible Rich Internet Applications)
- Complex widgets (e.g. using values from multiple fields) support
- Filter-forms (use form for queryset filtering)

Supported styling:

- No CSS
- Bootstrap 4
- Bootstrap 5

## Requirements

1. Python 3.10+
2. Django 3.2+

## Getting started

Install the package:

```shell
$ python -m pip install django-siteforms
```

Continue with the [Quickstart](010_quickstart.md) to create and process a Bootstrap 5 model form,
then read [Core concepts](015_core_concepts.md) for request binding, submission markers, multiple
forms, and rendering options. The other guides cover [Composers](020_composers/index.md), subforms,
[filtering forms](030_filtering/index.md), [field states and read-only views](035_field_states.md),
[Bootstrap-specific options](040_bootstrap/index.md), and the generated [API reference](090_api/index.md).
