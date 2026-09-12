# Many-to-many relations

A subform registered for a `ManyToManyField` is rendered as a Django model formset. Existing
related objects become initial forms, and extra forms can create related objects.

```python title="profiles/models.py"
from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=100)


class Profile(models.Model):
    name = models.CharField(max_length=100)
    skills = models.ManyToManyField(Skill)
```

```python title="profiles/forms.py"
from siteforms.composers.bootstrap5 import Bootstrap5
from siteforms.toolbox import ModelForm

from .models import Profile, Skill


class SkillForm(ModelForm):

    class Meta:
        model = Skill
        fields = ['name']


class ProfileForm(ModelForm):
    subforms = {
        'skills': SkillForm,
    }

    formset_kwargs = {
        'skills': {
            'extra': 2,
        },
    }

    class Composer(Bootstrap5):
        opt_submit = 'Save'

    class Meta:
        model = Profile
        fields = ['name', 'skills']
```

`formset_kwargs` is keyed by the parent field name. Each value is passed to Django's
`modelformset_factory()`. Options such as `extra`, `min_num`, `max_num`, `validate_min`, and
`validate_max` can therefore be configured per relation.

The generated formset uses names such as `skills-0-name`. Its management form is included in the
parent output automatically. If JavaScript adds or removes forms in the browser, it must follow
Django formset rules and update the management fields.

On an edit form, only objects currently related through `profile.skills` are included. Valid extra
forms create new `Skill` objects, and `ProfileForm.save()` saves the formset and the parent
relation.

For a custom intermediary model, expose a `ModelMultipleChoiceField` whose queryset contains the
intermediary objects, register a model form for that field, and exclude the original
`ManyToManyField` from the parent model form. This is an advanced setup; validate its queryset and
ownership constraints explicitly.
