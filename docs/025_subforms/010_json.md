# JSON-encoded values

A regular parent field can be represented by a plain `Form`. After validation, `siteforms`
serializes the subform's `cleaned_data` to JSON and passes it through the original parent field's
validation.

The following model stores a JSON string in a text field:

```python title="profiles/models.py"
from django.db import models


class Profile(models.Model):
    name = models.CharField(max_length=100)
    preferences = models.TextField(default='{}')
```

Define the structure of that value with a regular siteforms form:

```python title="profiles/forms.py"
from siteforms.composers.bootstrap5 import Bootstrap5
from siteforms.toolbox import Form, ModelForm, fields

from .models import Profile


class PreferencesForm(Form):
    theme = fields.ChoiceField(choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
    ])
    email_notifications = fields.BooleanField(required=False)


class ProfileForm(ModelForm):
    subforms = {
        'preferences': PreferencesForm,
    }

    class Composer(Bootstrap5):
        opt_submit = 'Save'

    class Meta:
        model = Profile
        fields = ['name', 'preferences']
```

The rendered controls are named `preferences-theme` and
`preferences-email_notifications`. Validating and saving the parent form stores a value similar
to:

```json
{"theme": "dark", "email_notifications": true}
```

When an existing `Profile` is edited, `preferences` must contain valid JSON text representing an
object. `siteforms` decodes that text and uses its keys as the subform's initial values.

!!! warning
    Malformed JSON already stored in the parent field cannot be used to initialize the subform.
    Validate externally produced values before storing them.

The child form may define its own `Composer`. If it does not, `siteforms` derives one from the
parent composer so that the nested controls use compatible styling.
