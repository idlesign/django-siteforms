# Field states and read-only views

`siteforms` can hide controls, disable them, or replace them with read-only values. These modes
affect rendering differently and must not be used interchangeably.

| Setting | Visible | Submitted value accepted | Rendered as a control |
|---|---:|---:|---:|
| `hidden_fields` | No | Yes | Hidden input |
| `disabled_fields` | Yes | No | Disabled input |
| `readonly_fields` | Yes | No | `ReadOnlyWidget` output |

Declare field names on the form class:

```python
class ArticleForm(ModelForm):
    hidden_fields = {'internal_code'}
    disabled_fields = {'status'}
    readonly_fields = {'published_at'}
```

The same settings can be passed to a form instance when the state depends on the current view or
user:

```python
form = ArticleForm(
    request=request,
    src='POST',
    instance=article,
    hidden_fields={'internal_code'},
    disabled_fields={'status'},
    readonly_fields={'published_at'},
)
```

Avoid placing one field in several state sets. Hidden rendering takes precedence over the visible
widget, while disabled and read-only processing still affects validation.

## Hidden fields

`hidden_fields` replaces the field widget with Django's `HiddenInput`. The value remains part of the
submitted form and is validated normally.

Hidden fields are not a security boundary. A client can modify their values, so authorization and
integrity checks must still happen on the server. Prefer excluding a field from `Meta.fields` when
the client should not control it at all.

Validation errors from hidden fields are added to the form's non-field feedback so that an invalid
hidden value does not fail silently.

`hidden_fields` expects a set of names. Unlike disabled and read-only fields, it does not support
the `__all__` shortcut.

## Disabled fields

`disabled_fields` uses Django's disabled-field behaviour. The control is visible with the
`disabled` attribute, submitted input for it is ignored, and validation uses the field's initial or
instance value.

```python
form = ArticleForm(
    request=request,
    src='POST',
    instance=article,
    disabled_fields={'status'},
)
```

This is suitable for an edit form that displays immutable data while preserving the value already
stored on the model. When creating an object, provide a valid initial value for a required disabled
field or exclude it from the form.

Use `__all__` to disable every field:

```python
form = ArticleForm(disabled_fields='__all__')
```

## Read-only fields

`readonly_fields` replaces the normal widget with `ReadOnlyWidget` and disables the field for
validation. This is display-only rendering, not the HTML `readonly` attribute:

```python
form = ArticleForm(
    instance=article,
    readonly_fields={'title', 'status'},
)
```

Use `__all__` to render every field as a value. Combined with `render_form_tag=False`, this provides
a lightweight detail view that reuses the edit form's layout:

```python
def article_detail(request, article):
    form = ArticleForm(
        request=request,
        instance=article,
        readonly_fields='__all__',
        render_form_tag=False,
    )
    return render(request, 'articles/detail.html', {'form': form})
```

The template can render `{{ form }}` without producing a nested `<form>` or submit button.

Pass `readonly_fields='__all__'` or `disabled_fields='__all__'` to the parent constructor when the
state must propagate into registered subforms. A class-level declaration applies to that form
class; child form classes can also declare their own field states.

## Custom read-only widgets

Map field names to `ReadOnlyWidget` subclasses with `Meta.widgets_readonly`. Values in the mapping
are widget classes, not instances:

```python
from django.utils.html import format_html

from siteforms.toolbox import ModelForm, ReadOnlyWidget


class StatusReadOnlyWidget(ReadOnlyWidget):

    def format_value_hook(self, value):
        return format_html('<strong>{}</strong>', value)


class ArticleForm(ModelForm):
    readonly_fields = {'status'}

    class Meta:
        model = Article
        fields = ['title', 'status']
        widgets_readonly = {
            'status': StatusReadOnlyWidget,
        }
```

`format_value_hook()` receives the value after field-specific formatting, including choice labels
and yes/no rendering for booleans. Escape untrusted content or use Django's `format_html()` when
returning markup.

Override `wrap_value()` to change the outer element:

```python
from django.forms.utils import flatatt
from django.utils.html import format_html


class InlineReadOnlyWidget(ReadOnlyWidget):

    @classmethod
    def wrap_value(cls, *, value, attrs):
        return format_html('<span{}>{}</span>', flatatt(attrs), value)
```

Attribute and escaping requirements are the responsibility of the custom implementation.

For a `ModelMultipleChoiceField`, override `get_multiple_items()` to optimize or reorder related
objects before they are formatted:

```python
class AuthorsReadOnlyWidget(ReadOnlyWidget):

    def get_multiple_items(self, value):
        if value is None:
            return []
        return list(value.select_related('profile').order_by('name'))
```

## Model property fields

`ModelForm` can populate explicitly declared fields from model properties. List those field names
in `Meta.property_fields`:

```python
from siteforms.toolbox import ModelForm, fields


class ArticleForm(ModelForm):
    word_count = fields.IntegerField(required=False)
    readonly_fields = {'word_count'}

    class Meta:
        model = Article
        fields = ['title', 'contents', 'word_count']
        property_fields = ['word_count']
```

If `Article.word_count` is a property, its value is copied into the form's initial data when an
instance is supplied. An explicitly provided `initial['word_count']` takes precedence.

Property fields must be declared on the form and included in `Meta.fields`. Mark calculated values
read-only or disabled when they must not be accepted from the client.
