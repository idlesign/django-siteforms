# Validation and saving

## Processing a request

Process a form containing subforms in the same way as any other siteforms model form:

```python
from django.db import transaction
from django.shortcuts import redirect, render

from .forms import ProfileForm


def profile_edit(request, profile):
    form = ProfileForm(
        request=request,
        src='POST',
        instance=profile,
    )

    if form.is_submitted:
        with transaction.atomic():
            if form.is_valid():
                profile = form.save()
                return redirect('profile-detail', pk=profile.pk)

            # A valid sibling subform may already have created a related
            # object while another part of the parent form failed.
            transaction.set_rollback(True)

    return render(request, 'profiles/edit.html', {'form': form})
```

The parent renderer emits nested fields, formset management fields, uploaded-file encoding, CSRF
token, and submit marker. The template can continue to use only `{{ form }}`.

## Validation order

Calling `is_valid()` on the parent form:

1. constructs and validates every registered subform;
2. passes each subform's cleaned value through the original parent field;
3. validates the remaining parent form fields;
4. returns `False` if either the parent or any subform is invalid.

Subform errors are rendered where the original parent field would be rendered. A file field at any
nested level also causes the parent `<form>` to use `enctype="multipart/form-data"`.

## Saving and transactions

For model forms, calling `save()` saves registered subforms before saving the parent form. Existing
foreign-key objects and many-to-many formset objects are updated as part of that call.

Creating a new foreign-key object or a new item from an extra many-to-many form can happen while
the parent is being cleaned during `is_valid()`. Therefore:

- wrap both `is_valid()` and `save()` in `transaction.atomic()` when the whole operation must be
  atomic, and mark the transaction for rollback when validation fails;
- do not use `commit=False` as a substitute for a transaction;
- validate authorization for related instances before constructing the form or its querysets.

## Accessing subforms

Use `get_subform()` when application code needs the instantiated child form:

```python
address_form = form.get_subform(name='address')
skills_formset = form.get_subform(name='skills')
first_skill_form = skills_formset.forms[0]
```

The method constructs a registered subform on first access and then returns the same instance for
the lifetime of the parent form. For nested access, first retrieve the immediate child and then
call its `get_subform()` method:

```python
address_form = form.get_subform(name='address')
country_form = address_form.get_subform(name='country')
```

Normally there is no reason to instantiate a registered subform directly: the parent supplies the
correct prefixes, request data, files, instance, and rendering mode.
