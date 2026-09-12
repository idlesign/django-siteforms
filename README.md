# django-siteforms

<https://github.com/idlesign/django-siteforms>

[![release](https://img.shields.io/pypi/v/django-siteforms.svg)](https://pypi.python.org/pypi/django-siteforms)
[![lic](https://img.shields.io/pypi/l/django-siteforms.svg)](https://pypi.python.org/pypi/django-siteforms)
[![coverage](https://img.shields.io/coveralls/idlesign/django-siteforms/master.svg)](https://coveralls.io/r/idlesign/django-siteforms)

Django reusable app that renders complete forms and reduces the amount of form-related template
code. It supports declarative layouts and attributes, Bootstrap 4 and 5, nested subforms,
read-only views, and queryset filtering forms.

## Installation

```shell
$ python -m pip install django-siteforms
```

Python 3.10 or newer and Django 3.2 or newer are required. See the
[tested compatibility matrix](https://django-siteforms.readthedocs.io/en/latest/#compatibility)
for the combinations covered by CI.

## Quick example

```python
from siteforms.composers.bootstrap5 import Bootstrap5
from siteforms.toolbox import ModelForm

from .models import Article


class ArticleForm(ModelForm):

    class Composer(Bootstrap5):
        opt_submit = 'Save'

    class Meta:
        model = Article
        fields = ['title', 'contents']
```

Pass the request and data source when constructing the form:

```python
form = ArticleForm(request=request, src='POST')

if form.is_submitted and form.is_valid():
    article = form.save()
```

Then render it directly:

```django
{{ form }}
```

The output includes the `<form>` wrapper, CSRF token, fields, and submit button. Start with the
[Quickstart](https://django-siteforms.readthedocs.io/en/latest/010_quickstart/) and continue with
the [full documentation](https://django-siteforms.readthedocs.io/).

## Development

Development tasks are provided by [makeapp](https://pypi.org/project/makeapp/). After cloning the
repository, install or update it and initialize the project:

```shell
$ uv tool install makeapp
# or: uv tool upgrade makeapp
$ ma tools
$ ma up
```

Run the same project checks before submitting a pull request:

```shell
$ ma style
$ ma tests
$ ma docs --build
```
