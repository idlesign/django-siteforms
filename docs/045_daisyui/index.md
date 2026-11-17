# DaisyUI

`django-siteforms` includes the `Daisyui` composer targeting DaisyUI 5 component classes on top of
Tailwind CSS 4. The generated markup requires no JavaScript.

The package does not include DaisyUI or Tailwind CSS assets. Load those assets in the application's
base template using the installation method recommended by the DaisyUI project.

```python
from siteforms.composers.daisyui import Daisyui
from siteforms.toolbox import Form, fields


class ContactForm(Form):
    email = fields.EmailField()
    message = fields.CharField(widget=fields.Textarea)

    class Composer(Daisyui):
        opt_submit = 'Send'
```

Fields are wrapped into `fieldset` containers with `label` classes applied to labels and help
texts, following the form structure suggested by DaisyUI.

## Sizes

Use the supplied constants:

```python
class Composer(Daisyui):
    opt_size = Daisyui.SIZE_SMALL
```

The size is applied to controls and the submit button (`input-sm`, `select-sm`, `btn-sm`, etc.).
`SIZE_NORMAL` is the default.

## Checkboxes and toggles

Boolean fields use the `checkbox` class. Render them as toggles with:

```python
class Composer(Daisyui):
    opt_checkbox_toggle = True
```

This changes presentation only; submitted and cleaned values follow Django's Boolean field rules.

## Validation feedback

After the form is submitted, invalid controls receive the corresponding `-error` color class
(`input-error`, `select-error`, etc.), and their errors are rendered with `text-error`.
Non-field errors use an alert with `role="alert"`.

Valid controls are not highlighted by default. Enable `opt_feedback_valid` to apply `-success`
classes to them:

```python
class Composer(Daisyui):
    opt_feedback_valid = True
```

!!! note
    The composer does not use DaisyUI's `validator`/`validator-hint` classes, as those rely on
    browser-native validation, while siteforms renders server-side feedback.

See the [Composer API](../020_composers/050_api.md) for defaults generated through `apidescribed`.
