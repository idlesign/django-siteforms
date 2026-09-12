# Filtering forms

Filtering forms validate query parameters and translate their cleaned values into Django queryset
lookups. Use `FilteringModelForm` when fields come from a model, or `FilteringForm` for a fully
custom filter interface.

## Complete example

Suppose an article has a title, publication status, and publication date:

```python title="articles/models.py"
from django.db import models


class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'

    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status)
    published_at = models.DateField(null=True, blank=True)
```

The filter form can combine model fields with additional range fields:

```python title="articles/forms.py"
from siteforms.composers.bootstrap5 import Bootstrap5
from siteforms.toolbox import FilteringModelForm, fields

from .models import Article


class ArticleFilterForm(FilteringModelForm):
    published_from = fields.DateField(label='Published from')
    published_until = fields.DateField(label='Published until')

    lookup_names = {
        'published_from': 'published_at',
        'published_until': 'published_at',
    }
    filtering_rules = {
        'title': 'icontains',
        'published_from': 'gte',
        'published_until': 'lte',
    }

    class Composer(Bootstrap5):
        opt_form_inline = True
        opt_submit = 'Filter'

    class Meta:
        model = Article
        fields = [
            'title',
            'status',
            'published_from',
            'published_until',
        ]
```

Filtering fields are optional by default, even when the corresponding model fields are required.
Choice fields also receive an initial `----` option that means "do not filter by this field".

Construct the form from `GET` and apply it to a base queryset:

```python title="articles/views.py"
from django.shortcuts import render

from .forms import ArticleFilterForm
from .models import Article


def article_list(request):
    filter_form = ArticleFilterForm(
        request=request,
        src='GET',
        prefix='filter',
        id='article-filter',
    )
    articles, filter_applied = filter_form.filtering_apply(
        Article.objects.all(),
    )

    return render(request, 'articles/list.html', {
        'articles': articles,
        'filter_applied': filter_applied,
        'filter_form': filter_form,
    })
```

Render the GET form and the resulting queryset:

```django title="articles/templates/articles/list.html"
{{ filter_form }}

{% if filter_applied %}
  <p>Filters are active.</p>
{% endif %}

{% for article in articles %}
  <article>{{ article.title }}</article>
{% empty %}
  <p>No articles found.</p>
{% endfor %}
```

A request may look like:

```text
?filter-title=django&filter-status=published&__submit=filter
```

The prefix is part of each field name. The generated submit button uses the same prefix as its
marker, allowing `siteforms` to distinguish this filter from other forms on the page.

## Result of `filtering_apply()`

`filtering_apply(queryset)` returns `(queryset, applied)`:

- valid non-empty values produce a filtered queryset and `applied=True`;
- a valid form without filter values produces an equivalent unfiltered queryset and
  `applied=False`;
- invalid input returns the original queryset and `applied=False`.

In the invalid case, form errors remain available and are rendered with the filtering form. Do not
replace an invalid form with a new instance before rendering the response.

## More guides

- [Field names and lookup rules](010_lookups.md)
- [Optional fields and undefined choices](020_choices.md)
- [Initial and request values](030_initial.md)
- [Multiple filters, safety, and performance](040_usage.md)
