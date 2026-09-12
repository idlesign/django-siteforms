# Quickstart

This guide creates a Bootstrap 5 form for adding an article. The rendered result includes the
`<form>` element, CSRF token, fields, validation feedback, and submit button.

## Installation

Install `django-siteforms` into your Django project:

```shell
$ python -m pip install django-siteforms
```

The examples below assume that Bootstrap 5 CSS is already loaded by the base template. The package
generates Bootstrap-compatible markup but does not bundle Bootstrap assets.

## Model

Start with a regular Django model:

```python title="articles/models.py"
from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=200)
    contents = models.TextField()
```

Create and apply a migration after adding the model:

```shell
$ python manage.py makemigrations
$ python manage.py migrate
```

## Form

Inherit from the `ModelForm` exposed by `siteforms.toolbox` and declare a nested composer. The
composer controls how the form is rendered; validation and saving still follow Django's regular
`ModelForm` behaviour.

```python title="articles/forms.py"
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

`Bootstrap5` produces Bootstrap 5 markup. `opt_submit` defines the label of the submit button that
`siteforms` adds to the rendered form.

## View

Pass the current request and the data source to the form:

```python title="articles/views.py"
from django.shortcuts import redirect, render

from .forms import ArticleForm


def article_create(request):
    form = ArticleForm(request=request, src='POST')

    if form.is_submitted and form.is_valid():
        article = form.save()
        return redirect('article-detail', pk=article.pk)

    return render(request, 'articles/create.html', {'form': form})
```

On a GET request the form remains unbound. On a POST request, `siteforms` uses its generated submit
button to determine whether this particular form was submitted and exposes the result through
`is_submitted`. Once submitted, `is_valid()` and `save()` behave like their Django counterparts.

Using `is_submitted` rather than only checking `request.method` matters when a page contains more
than one form.

## URL

Connect the view using Django's URL dispatcher:

```python title="articles/urls.py"
from django.urls import path

from .views import article_create


urlpatterns = [
    path('new/', article_create, name='article-create'),
]
```

## Template

Render the form variable directly:

```django title="articles/templates/articles/create.html"
{% extends "base.html" %}

{% block content %}
  <div class="container py-4">
    <h1>Add article</h1>
    {{ form }}
  </div>
{% endblock %}
```

There is no need to add `{% csrf_token %}`, `<form>`, or a submit button in this template. For a
form configured with `src='POST'`, `siteforms` adds all three when it receives `request`.

If you disable the form wrapper using `render_form_tag=False`, the surrounding template becomes
responsible for the `<form>` element, CSRF token, and submit control.

Continue with [Advanced](020_advanced.md) for custom layouts and subforms, or with
[Filtering Forms](030_filtering.md) to build a queryset filter.
