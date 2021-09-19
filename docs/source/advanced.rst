Advanced
========

``Composers`` allows declarative configuration with the help of class attributes which
should be enough for many simple cases.

Just inherit from your composer from base composer class and set attributes and options you want to override.

.. code-block:: python

    from siteforms.composers.bootstrap4 import Bootstrap4


    class Composer(Bootstrap4):

        opt_render_labels = False
        opt_placeholder_label = True

        attrs_help = {'class': 'some', 'data-one': 'other'}


Attributes
----------

* ``attrs`` - Attributes to apply to basic elements (form, fields, widget types, groups).

* ``attrs_labels`` - Attributes to apply to labels.

* ``attrs_help`` - Attributes to apply to hints.

* ``attrs_feedback`` - Attributes to apply to feedback (validation notes).

* ``wrappers`` - Wrappers for fields, groups, rows, submit button.

* ``groups`` - Map alias to group titles. Groups can be addressed in ``layout``.

* ``layout`` - Layout instructions for fields and form.


Options
-------

* ``opt_form_inline`` - Make form inline.

* ``opt_render_form_tag`` - Render form tag. On by default.

* ``opt_label_colon`` - Whether to render colons after label's texts.

* ``opt_render_labels`` - Render label elements.

* ``opt_render_help`` - Render hints (help texts).

* ``opt_placeholder_label`` - Put title (verbose name) into field's placeholders.

* ``opt_placeholder_help`` - Put hint (help text) into field's placeholders.

* ``opt_title_label`` - Put title (verbose name) into field's title.

* ``opt_title_help`` - Put hint (help text) into field's title.

* ``opt_tag_help`` - Tag to be used for hints.

* ``opt_tag_feedback`` - Tag to be used for feedback.

* ``opt_submit`` - Submit button text. If not set, submit button won't be added into this form.

* ``opt_submit_name`` - Submit button name.


Macroses
--------

Macroses are a quick way to address various objects.

They can be used as keys in ``Attributes`` (see above).

* ``ALL_FIELDS`` - Denotes every field.

* ``ALL_GROUPS`` - Denotes every group.

* ``ALL_ROWS`` - Denotes every row.

* ``FORM`` - Denotes a form.

* ``SUBMIT`` - Submit button.


ALL_FIELDS in Layout
--------------------

``ALL_FIELDS`` macros can be used in many places in layout.
It expands into rows for each field which has not been addressed so far.

As layout value
~~~~~~~~~~~~~~~

This one is the default.

.. code-block:: python

        layout = {
            FORM: ALL_FIELDS
        }


As group value
~~~~~~~~~~~~~~

.. code-block:: python

        layout = {
            FORM: {
                'basic': [  # group
                    ['title', 'date_created'],  # row1
                    'contents',  # row2
                ],
                'other': ALL_FIELDS,  # rest rows
            }
        }



As group row
~~~~~~~~~~~~

.. code-block:: python

        layout = {
            FORM: {
                'basic': [  # group
                    ['title', 'date_created'],  # row1
                    ALL_FIELDS,  # rest rows
                ],
            }
        }


Subforms
--------

Sometimes you may want to represent an entire other form as a field of you main form.

This can be considered as an alternative to complex widgets.

.. code-block:: python

    from siteforms.composers.bootstrap4 import Bootstrap4
    from siteforms.toolbox import ModelForm, Form

    class SubForm(Form):
        """This form we'll include in our main form."""

        class Composer(Bootstrap4):

            opt_render_labels = False
            opt_placeholder_label = True

        field1 = fields.CharField(label='field1')
        field2 = fields.ChoiceField(label='field1')

        def get_subform_value(self):
            """You may override this method to apply value casting.
            Be default it returns subform's cleaned data dictionary
            (convenient for JSONField in main form).

            The result of this method would became the value of main form field.

            """
            value = super().get_subform_value()
            return f"{value['field1']} ----> {value['field2']}"

    class MyForm(ModelForm):
        """That would be our main form.

        Let's suppose it has `myfield` field, which value
        we want to represent in a subform.

        """
        subforms = {'myfield': SubForm}  # Map field name to subform class.

        class Composer(Bootstrap4):

            opt_columns =  True

        class Meta:
            model = MyModel
            fields = '__all__'


After MyForm instance is validated (``.is_valid()``), subform fields values
are gathered (see ``.get_subform_value()``) and placed into main form ``cleaned_data``.


Multiple forms
--------------
You may put more than one form from the same view.

For that to wok properly please use ``prefix`` for your forms.

.. code-block:: python

    form1 = MyForm1()
    form2 = MyForm2(prefix='form2')
    form3 = MyForm3(prefix='form3')

Prefix attribute may also be declared in form class.
