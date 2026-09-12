# Field names and lookup rules

Each non-empty cleaned form value becomes a keyword argument for `QuerySet.filter()`. By default,
the form field name is also the model lookup name and no lookup suffix is added.

```python
class ArticleFilterForm(FilteringModelForm):

    class Meta:
        model = Article
        fields = ['status']
```

A submitted status therefore produces the equivalent of:

```python
queryset.filter(status=cleaned_status)
```

## Lookup rules

Use `filtering_rules` to add a Django lookup suffix for a form field:

```python
filtering_rules = {
    'title': 'icontains',
    'published_from': 'gte',
    'published_until': 'lte',
}
```

For example, the `title` value becomes `title__icontains=value`.

A rule can contain transforms and a final lookup:

```python
filtering_rules = {
    'created_year': 'year__gte',
}
```

## Mapping form fields to model fields

Use `lookup_names` when the form field name does not match the queryset field path:

```python
lookup_names = {
    'author_name': 'author__name',
    'published_from': 'published_at',
    'published_until': 'published_at',
}
```

`lookup_names` is applied first and `filtering_rules` is appended afterwards. With both mappings,
`published_from` can produce:

```python
queryset.filter(published_at__gte=cleaned_published_from)
```

## Multiple values

Use a multiple-choice field together with the `in` lookup:

```python
from siteforms.composers.bootstrap5 import Bootstrap5
from siteforms.toolbox import FilteringForm, fields

from .models import Article


class ArticleFilterForm(FilteringForm):
    statuses = fields.MultipleChoiceField(choices=Article.Status.choices)

    lookup_names = {
        'statuses': 'status',
    }
    filtering_rules = {
        'statuses': 'in',
    }

    class Composer(Bootstrap5):
        opt_submit = 'Filter'
```

A query string with repeated values is preserved by Django's `QueryDict` and becomes a list passed
to `status__in`:

```text
?statuses=draft&statuses=published&__submit=siteform
```

## Date range

Two form fields can target one model field using different rules:

```python
published_from = fields.DateField()
published_until = fields.DateField()

lookup_names = {
    'published_from': 'published_at',
    'published_until': 'published_at',
}
filtering_rules = {
    'published_from': 'gte',
    'published_until': 'lte',
}
```

Both values are cleaned as dates before they reach the queryset.
