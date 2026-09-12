# Reusable and custom composers

Composer classes are regular Python classes. Put project-wide defaults in a reusable subclass and
derive form-specific nested composers from it.

## Project defaults

```python title="project/composers.py"
from siteforms.composers.base import ALL_FIELDS, SUBMIT
from siteforms.composers.bootstrap5 import Bootstrap5


class ProjectComposer(Bootstrap5):
    opt_label_colon = False
    attrs = {
        ALL_FIELDS: {
            'data-project-control': 'true',
        },
        SUBMIT: {
            'class': 'btn btn-success',
        },
    }
```

Use it from individual forms:

```python
from project.composers import ProjectComposer
from siteforms.toolbox import Form, fields


class ContactForm(Form):
    email = fields.EmailField()
    message = fields.CharField(widget=fields.Textarea)

    class Composer(ProjectComposer):
        opt_submit = 'Send'
        attrs = {
            'message': {
                'rows': 8,
            },
        }
```

The nested composer retains inherited mappings and overrides only the specified keys.

## No-framework markup

Use `FormComposer` directly when the project supplies all styling itself:

```python
from siteforms.composers.base import ALL_FIELDS, FormComposer
from siteforms.toolbox import Form, fields


class PlainComposer(FormComposer):
    wrappers = {
        ALL_FIELDS: '<div class="field">{field}</div>',
    }


class ContactForm(Form):
    email = fields.EmailField()

    class Composer(PlainComposer):
        pass
```

The base composer still provides complete form rendering, submission markers, CSRF handling,
accessible labels and help links, and validation feedback. It simply does not apply Bootstrap
classes.

## Runtime customization

Override `get_composer()` on the form only when class-level declarations are insufficient. Always
start from the configured composer so that inherited behaviour remains intact:

```python
class ContactForm(Form):
    email = fields.EmailField()

    class Composer(ProjectComposer):
        pass

    def get_composer(self):
        composer = super().get_composer()
        composer.opt_submit = f'Send to {self.initial.get("department", "support")}'
        return composer
```

Prefer declarative settings and callable attribute values for isolated dynamic attributes. A
`get_composer()` override is most useful when several settings depend on the form instance.
