# File uploads and external form tags

## Automatic form wrapper

Define file fields normally:

```python
from siteforms.composers.bootstrap5 import Bootstrap5
from siteforms.toolbox import ModelForm


class DocumentForm(ModelForm):

    class Composer(Bootstrap5):
        opt_submit = 'Upload'

    class Meta:
        model = Document
        fields = ['title', 'attachment']
```

Passing `request` and `src='POST'` binds both `request.POST` and `request.FILES`:

```python
def document_create(request):
    form = DocumentForm(request=request, src='POST')

    if form.is_submitted and form.is_valid():
        document = form.save()
        return redirect('document-detail', pk=document.pk)

    return render(request, 'documents/create.html', {'form': form})
```

`{{ form }}` automatically includes `enctype="multipart/form-data"`. File fields inside nested
subforms are detected too.

## External form wrapper

Use `render_form_tag=False` when siteforms fields must live inside an existing form element:

```python
form = DocumentForm(
    request=request,
    src='POST',
    render_form_tag=False,
)
```

The template must reproduce every removed responsibility:

```django
<form method="post" enctype="multipart/form-data">
  {% csrf_token %}
  {{ form }}
  <button type="submit" name="__submit" value="siteform">Upload</button>
</form>
```

Use the form's prefix or explicit `submit_marker` as the button value when it differs from
`siteform`. If the composer changes `opt_submit_name`, change the button name as well.

## Custom action

Use `target_url` instead of writing a wrapper only to change the form action:

```python
form = DocumentForm(
    request=request,
    src='POST',
    target_url=reverse('document-upload'),
)
```

The generated form receives the corresponding `action` attribute while keeping automatic CSRF,
multipart, and submission handling.
