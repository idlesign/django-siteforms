# Filtering defaults

Use `initial` when a listing should start with an active default filter:

```python
filter_form = ArticleFilterForm(
    request=request,
    src='GET',
    prefix='filter',
    initial={
        'status': 'published',
    },
)
articles, filter_applied = filter_form.filtering_apply(
    Article.objects.all(),
)
```

On a request without `filter-status`, published articles are selected and `filter_applied` is
`True`. A request value overrides the default:

```text
?filter-status=draft
```

To offer a visible way to clear the default, submit an explicit empty value or the filtering
form's undefined-choice marker. Choice fields receive that marker automatically by default.

For several defaults, include each unprefixed form field name in `initial`:

```python
from datetime import date, timedelta


initial={
    'published_from': date.today() - timedelta(days=30),
    'statuses': ['draft', 'published'],
}
```

Request values are merged per field, and multiple-choice lists are preserved. See
[Initial and request values](../030_filtering/030_initial.md) and
[Optional fields and undefined choices](../030_filtering/020_choices.md) for details.
