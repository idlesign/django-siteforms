Filtering Forms
===============

``siteforms`` allows you to use form a filter applied to a query set.

Use ``FilteringForm`` or ``FilteringModelForm``.

.. code-block:: python

    from siteforms.composers.bootstrap5 import Bootstrap5
    from siteforms.toolbox import FilteringModelForm

    # Let's suppose we want to filter articles we have in our database.
    # Among others fields Article model has `title` and `status`
    # we want our articles to be filtered by.

    # We inherit our form from FilteringModelForm.
    class MyFilterForm(FilteringModelForm):

        class Composer(Bootstrap5):  # apply styling as it fits our needs
            opt_form_inline = True

        class Meta:
            model = Article
            fields = ['title', 'status']

    # In our view function:
    filter_form = MyFilterForm(request=request, src='GET', id='flt')

    query_set = Article.objects.all()

    # Now we apply filter to our query set
    listing, filter_applied = filter_form.filtering_apply(query_set)

