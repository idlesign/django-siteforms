# Initial and request values

Pass `initial` to apply default filters when the request does not contain values for those fields:

```python
filter_form = ArticleFilterForm(
    request=request,
    src='GET',
    prefix='filter',
    initial={
        'status': 'published',
    },
)
```

Unlike display-only initial data on a regular Django form, these values participate in filtering.
If no relevant query parameter is present, `siteforms` prepares the initial value as submitted
data, validates it, and sets `filter_applied=True` when it produces a lookup.

Values explicitly present in the selected request source take precedence:

```text
?filter-status=draft
```

With the example above, the request filters by `draft`, not by the initial `published` value.

Prefixes are applied automatically when looking for request values. Pass unprefixed field names in
the `initial` dictionary:

```python
initial={'status': 'published'}  # Not {'filter-status': 'published'}.
```

Multiple values are supported. Field preparation runs before binding, so a multiple-choice initial
value should be a list or tuple:

```python
initial={
    'statuses': ['draft', 'published'],
}
```

Preparing filter data does not mutate `request.GET` or `request.POST`; the form works with its own
copy.

Initial filters are applied only when `request.method` matches `src`. Use `src='GET'` for normal
list and search pages.
