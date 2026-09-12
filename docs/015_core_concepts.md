# Core concepts

`django-siteforms` keeps Django's form validation and model-form saving APIs, and adds a rendering
composer plus request-aware form binding. Understanding those two additions makes the rest of the
library predictable.

## Forms and composers

Use the form classes from `siteforms.toolbox` instead of importing their Django counterparts:

```python
from siteforms.composers.bootstrap5 import Bootstrap5
from siteforms.toolbox import Form, fields


class ContactForm(Form):
    email = fields.EmailField()
    message = fields.CharField(widget=fields.Textarea)

    class Composer(Bootstrap5):
        opt_submit = 'Send'
```

The form owns fields, data, validation, and cleaned values. Its nested `Composer` owns HTML layout,
attributes, wrappers, help text, validation feedback, and the submit button.

Use `FormComposer` from `siteforms.composers.base` when no CSS framework is required, or use
`Bootstrap4` or `Bootstrap5` for framework-compatible markup.

Render the custom composer output with `{{ form }}` in a template or `str(form)` in Python.
Django helpers such as `as_p()` request Django's own form templates instead.

## Request and data source

Pass both `request` and `src` to let `siteforms` bind request data and render a complete form:

```python
form = ContactForm(request=request, src='POST')
```

`src` names an `HttpRequest` attribute and must use the same uppercase spelling as
`request.method` when the form is submitted.

| Configuration | Rendered method | Automatic data source | CSRF token |
|---|---|---|---|
| `src='POST'` | `POST` | `request.POST` and `request.FILES` | Included |
| `src='GET'` | `GET` | `request.GET` | Not included |
| `src` omitted | `POST` | None | Not included |

Automatic binding occurs only when the selected source contains this form's submit marker and
`request.method` matches `src`. Consequently, a regular POST form remains unbound while displaying
its initial GET response.

`src='GET'` is primarily useful for filtering and search forms. See
[Filtering Forms](030_filtering.md) for the filtering-specific workflow.

## Submission markers

The generated submit button identifies which form was submitted. By default, it has the following
name and value:

```html
<button type="submit" name="__submit" value="siteform">Submit</button>
```

When the marker is found, `form.is_submitted` becomes `True` and request data is bound to the form:

```python
form = ContactForm(request=request, src='POST')

if form.is_submitted and form.is_valid():
    send_message(**form.cleaned_data)
```

Set `submit_marker` when an explicit value is useful:

```python
form = ContactForm(
    request=request,
    src='POST',
    submit_marker='contact',
)
```

The submit button name comes from `Composer.opt_submit_name`, while its value comes from
`form.submit_marker`. If no explicit marker is given, the form prefix is used, falling back to
`siteform` for an unprefixed form.

## Multiple forms on one page

Give each form a unique Django `prefix`. It separates field names and also supplies a distinct
default submit marker:

```python
profile_form = ProfileForm(
    request=request,
    src='POST',
    prefix='profile',
    instance=request.user.profile,
)
password_form = PasswordForm(
    request=request,
    src='POST',
    prefix='password',
    user=request.user,
)

if profile_form.is_submitted and profile_form.is_valid():
    profile_form.save()

if password_form.is_submitted and password_form.is_valid():
    password_form.save()
```

The first form renders names such as `profile-display_name` and a submit button whose value is
`profile`. The second uses the `password-` field prefix and the `password` marker. Only the form
whose button submitted the request becomes bound.

## `id`, `prefix`, and `target_url`

These constructor arguments solve different problems:

| Argument | Purpose |
|---|---|
| `id` | Sets the `<form id="...">` value and the generated IDs of its controls. |
| `prefix` | Adds Django's prefix to submitted field names and changes the default submit marker. |
| `target_url` | Sets the `<form action="...">` destination. |

For example:

```python
from django.urls import reverse


form = ContactForm(
    request=request,
    src='POST',
    id='contact-editor',
    prefix='contact',
    target_url=reverse('contact'),
)
```

`id` does not isolate submitted values. Use `prefix`, rather than only `id`, whenever multiple
forms contain fields with the same names. If `target_url` is omitted, the browser submits to the
current URL.

## Explicit data and files

Regular Django positional and keyword arguments remain available. When explicit data is supplied
together with request-aware binding, `siteforms` merges it with the selected request source and
explicit values take precedence:

```python
form = ContactForm(
    {'email': known_email},
    request=request,
    src='POST',
)
```

The same rule applies to explicitly supplied `files`. This is useful when application code needs
to augment or override a submitted value, but passing only `request` and `src` is clearer for the
usual view workflow.

## Form tag, CSRF, and file uploads

By default, the composer wraps fields in a `<form>`, adds the submit button, and adds a CSRF token
for `POST` forms constructed with a request. If the form or any nested subform contains a file
field, it also adds `enctype="multipart/form-data"`.

Disable the wrapper for embedding fields in an existing form element:

```python
form = ContactForm(
    request=request,
    src='POST',
    render_form_tag=False,
)
```

This can also be configured as `Composer.opt_render_form_tag = False`. In either case, the custom
template becomes responsible for the form element, action, method, CSRF token, multipart encoding,
and a submit button with the expected marker:

```django
<form method="post">
  {% csrf_token %}
  {{ form }}
  <button type="submit" name="__submit" value="siteform">Send</button>
</form>
```

When using a prefix or explicit `submit_marker`, use the corresponding value in the custom button.
