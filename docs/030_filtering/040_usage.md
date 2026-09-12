# Multiple filters, safety, and performance

## More than one filter form

As with other siteforms forms, assign a unique prefix to each filter form on the page:

```python
article_filter = ArticleFilterForm(
    request=request,
    src='GET',
    prefix='articles',
)
author_filter = AuthorFilterForm(
    request=request,
    src='GET',
    prefix='authors',
)
```

The generated submit markers distinguish which filter was submitted. Apply only the active form
when the two forms control separate listings:

```python
articles = Article.objects.all()
if article_filter.is_submitted:
    articles, article_filter_applied = article_filter.filtering_apply(articles)
```

An `id` changes HTML IDs but does not separate submitted values. Use `prefix` for isolation; add
`id` only when CSS or JavaScript also needs a stable form identifier.

## Combining filters

Every non-empty valid field is passed in the same `QuerySet.filter()` call, so conditions are
combined with SQL `AND`. For `OR`, conditional `Q` objects, annotations, or lookup behaviour that
depends on several fields, validate inputs with the filtering form and apply the custom queryset
logic in the view or a dedicated service.

## Invalid input

Invalid input never partially filters the queryset. If any field is invalid,
`filtering_apply()` returns the original queryset and `False`. Render the same form instance to
show its validation feedback.

## Lookup safety

Keep `lookup_names` and `filtering_rules` as developer-controlled declarations. Never copy lookup
paths or suffixes directly from request parameters. Form fields validate values, but arbitrary
lookup names can expose unintended relations or expensive database operations.

Restrict choice querysets and relation paths according to the current user's permissions before
applying the filter.

## Query performance

Filtering remains lazy because the result is a Django queryset. Normal Django optimization rules
apply:

- index fields used by frequent exact, range, and ordering operations;
- inspect searches such as `icontains`, which commonly require database-specific indexes for
  large tables;
- expect relationship paths in `lookup_names` to add joins;
- call `distinct()` explicitly when filtering across multi-valued relations can duplicate parent
  rows;
- apply `select_related()` or `prefetch_related()` according to how the resulting objects are
  rendered.

`filtering_apply()` does not add ordering, `distinct()`, eager loading, or pagination automatically.
