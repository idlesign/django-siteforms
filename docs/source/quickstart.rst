Quickstart
==========

Let's show how to build a simple form.

.. code-block:: python

    from django.shortcuts import render
    from siteforms.composers.bootstrap4 import Bootstrap4
    from siteforms.toolbox import ModelForm


    class MyForm(ModelForm):
        """This form will show us how siteforms works."""

        disabled_fields = {'somefield'}
        """One way of disabling fields. Use __all__ to disable all fields (affects subforms).
        This can also be passed into __init__() as the keyword-argument with the same name.

        """

        hidden_fields = {'otherfield'}
        """One way of hiding fields.
        This can also be passed into __init__() as the keyword-argument with the same name.

        """

        readonly_fields = {'anotherfield'}
        """One way of making fields readonly (to not to render input fields, but show a value).
        Use __all__ to make all fields readonly (affects subforms).
        This can also be passed into __init__() as the keyword-argument with the same name.

        """

        class Composer(Bootstrap4):
            """This will instruct siteforms to compose this
            form using Bootstrap 4 styling.

            """
        class Meta:
            model = MyModel  # Suppose you have a model class already.
            fields = '__all__'

    def my_view(request):
        # Initialize form using data from POST.
        my_form = MyForm(request=request, src='POST')
        is_valid = form.is_valid()
        return render(request, 'mytemplate.html', {'form': my_form})


Composer options
~~~~~~~~~~~~~~~~

Now let's see how to tune our form.

.. code-block:: python

    from siteforms.composers.bootstrap4 import Bootstrap4, FORM, ALL_FIELDS

    class Composer(Bootstrap4):

        opt_size='sm'  # Bootstrap 4 has sizes, so let's make our form small.

        # Element (fields, groups, form, etc.) attributes are ruled by `attrs`.
        # Let's add rows=2 to our `contents` model field.
        attrs={'contents': {'rows': 2}}

        # To group fields into named groups describe them in `groups`.
        groups={
            'basic': 'Basic attributes',
            'other': 'Other fields',
        }

        # We apply custom layout to our form.
        layout = {
            FORM: {
                'basic': [  # First we place `basic` group.
                    # The following three fields are in the same row -
                    # two fields in the right column are stacked.
                    ['title', ['date_created',
                               'date_updated']],
                    'contents',  # This one field goes into a separate row.
                ],
                # We place all the rest fields into `other` group.
                'other': ALL_FIELDS,
            }
        }

