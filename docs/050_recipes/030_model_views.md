# Create, edit, and detail views

One siteforms `ModelForm` can support create, edit, and display-only pages.

```python title="articles/forms.py"
from siteforms.composers.bootstrap5 import Bootstrap5
from siteforms.toolbox import ModelForm


class ArticleForm(ModelForm):

    class Composer(Bootstrap5):
        opt_submit = 'Save'

    class Meta:
        model = Article
        fields = ['title', 'status', 'contents']
```

## Create

```python
def article_create(request):
    form = ArticleForm(request=request, src='POST')

    if form.is_submitted and form.is_valid():
        article = form.save()
        return redirect('article-detail', pk=article.pk)

    return render(request, 'articles/form.html', {'form': form})
```

## Edit

```python
def article_edit(request, article):
    form = ArticleForm(
        request=request,
        src='POST',
        instance=article,
    )

    if form.is_submitted and form.is_valid():
        article = form.save()
        return redirect('article-detail', pk=article.pk)

    return render(request, 'articles/form.html', {'form': form})
```

## Detail

```python
def article_detail(request, article):
    form = ArticleForm(
        instance=article,
        readonly_fields='__all__',
        render_form_tag=False,
    )
    return render(request, 'articles/detail.html', {'form': form})
```

The detail view reuses field ordering, grouping, labels, choice formatting, and custom read-only
widgets without rendering editable controls or a form wrapper.

When registered subforms must also become read-only, pass `readonly_fields='__all__'` to the parent
constructor as shown. For custom output, see
[Field states and read-only views](../035_field_states.md).
