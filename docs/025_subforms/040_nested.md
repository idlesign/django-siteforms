# Nested subforms

A subform class may declare its own `subforms` mapping. `siteforms` carries the parent prefix,
request data, files, field state, and submit marker through every level.

For example, an address may contain a foreign-key relation to a country:

```python title="profiles/forms.py"
from siteforms.composers.bootstrap5 import Bootstrap5
from siteforms.toolbox import ModelForm

from .models import Address, Country, Profile


class CountryForm(ModelForm):

    class Meta:
        model = Country
        fields = ['name']


class AddressForm(ModelForm):
    subforms = {
        'country': CountryForm,
    }

    class Meta:
        model = Address
        fields = ['city', 'street', 'country']


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

The nested country control is named `address-country-name`. Calling `is_valid()` on the profile
validates both nested forms. Calling `save()` propagates saving through the same hierarchy.

The same mechanism works when the first level is a many-to-many formset. In that case names include
the formset index, for example `offices-0-country-name`.

If `readonly_fields='__all__'` or `disabled_fields='__all__'` is passed to the parent constructor,
the state is propagated to nested forms. Class-level settings and per-field sets apply to the form
class on which they are declared.
