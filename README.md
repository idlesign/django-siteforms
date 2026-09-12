# django-siteforms

<https://github.com/idlesign/django-siteforms>

[![release](https://img.shields.io/pypi/v/django-siteforms.svg)](https://pypi.python.org/pypi/django-siteforms) [![lic](https://img.shields.io/pypi/l/django-siteforms.svg)](https://pypi.python.org/pypi/django-siteforms) [![coverage](https://img.shields.io/coveralls/idlesign/django-siteforms/master.svg)](https://coveralls.io/r/idlesign/django-siteforms)

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

## Usage

Install the package:

```shell
$ python -m pip install django-siteforms
```

To render a form in a template, output the form variable, e.g. `<div>{{ form }}</div>`.

!!! note
    By default there is no need to add a submit button, a CSRF token, or a `<form>` wrapper.
    `siteforms` renders them automatically when the form receives the request and uses `POST` as
    its data source.

### Basic

Let's show how to build a simple form.

```python
from django.shortcuts import redirect, render
from siteforms.composers.bootstrap5 import Bootstrap5
from siteforms.toolbox import ModelForm

from .models import Article


class ArticleForm(ModelForm):

    class Composer(Bootstrap5):
        opt_submit = 'Save'

    class Meta:
        model = Article
        fields = ['title', 'contents']


def article_create(request):
    form = ArticleForm(request=request, src='POST')
    if form.is_submitted and form.is_valid():
        article = form.save()
        return redirect('article-detail', pk=article.pk)

    return render(request, 'articles/create.html', {'form': form})
```

The template only needs to render the form:

```django
<div class="container">
  {{ form }}
</div>
```

See the [Quickstart](https://django-siteforms.readthedocs.io/en/latest/010_quickstart/) for a
complete example.

### Composer options

Now let's see how to tune our form.

```python
from siteforms.composers.bootstrap5 import Bootstrap5, FORM, ALL_FIELDS


class Composer(Bootstrap5):

    opt_size = 'sm'  # Bootstrap 5 has sizes, so let's make our form small.

    # Element (fields, groups, form, etc.) attributes are ruled by `attrs`.
    # Let's add rows=2 to our `contents` model field.
    attrs = {'contents': {'rows': 2}}

    # To group fields into named groups describe them in `groups`.
    groups = {
        'basic': 'Basic attributes',
        'other': 'Other fields',
    }

    # We apply custom layout to our form.
    layout = {
        FORM: {
            'basic': [  # First we place `basic` group.
                # The following three fields are in the same row -
                # two fields in the right column are stacked.
                ['title', ['date_created',
                           'date_updated']],
                'contents',  # This one field goes into a separate row.
            ],
            # We place all the rest fields into `other` group.
            'other': ALL_FIELDS,
        }
    }
```

## Development

Use [makeapp](https://pypi.org/project/makeapp/) to streamline the development:

```shell
$ uv tool install makeapp
# or
$ uv tool upgrade makeapp
```

Clone the source code repository and switch into its directory:

```shell
# bootstrap the utilities
$ ma tools
# initialize the environment
$ ma up
```

Check code style and run tests before your pull request:

```shell
$ ma style
$ ma tests
$ ma docs --build
```

## Documentation

<https://django-siteforms.readthedocs.io/>
