# Foreign keys

A `ForeignKey` parent field can be represented by a siteforms `ModelForm`. This lets the user edit
the related object inline instead of choosing it from a select control.

```python title="profiles/models.py"
from django.db import models


class Address(models.Model):
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=200)


class Profile(models.Model):
    name = models.CharField(max_length=100)
    address = models.ForeignKey(
        Address,
        null=True,
        on_delete=models.CASCADE,
    )
```

Register the related model form under the foreign-key field name:

```python title="profiles/forms.py"
from siteforms.composers.bootstrap5 import Bootstrap5
from siteforms.toolbox import ModelForm

from .models import Address, Profile


class AddressForm(ModelForm):

    class Meta:
        model = Address
        fields = ['city', 'street']


class ProfileForm(ModelForm):
    subforms = {
        'address': AddressForm,
    }

    class Composer(Bootstrap5):
        opt_submit = 'Save'

    class Meta:
        model = Profile
        fields = ['name', 'address']
```

For an existing profile, the subform is initialized with `profile.address`. Calling
`ProfileForm.save()` updates both the address and the profile.

If the parent instance has no address, valid subform data creates an `Address` and assigns it to
the parent. See [Validation and saving](050_lifecycle.md) before relying on transaction boundaries
or `commit=False` for this case.

The related form is rendered with the `address-` prefix, so submitted field names include
`address-city` and `address-street`. Prefixing is automatic; do not set a prefix on `AddressForm`.
