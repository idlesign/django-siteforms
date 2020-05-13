Bootstrap 4
===========

To use Bootstrap 4 styling add ``Bootstrap4`` inherited composer in your form class.

.. code-block:: python

    from siteforms.composers.bootstrap4 import Bootstrap4


    class Composer(Bootstrap4):
        """This will instruct siteforms to compose this
        form using Bootstrap 4 styling.

        """


Options
-------

* ``opt_form_inline`` - Make form inline.

* ``opt_columns`` - Enabled two-columns mode.

  Expects a columns tuple: (label_columns_count, control_columns_count).

  If `True` default tuple ('col-2', 'col-10') is used.

* ``opt_custom_controls`` - Use custom controls from Bootstrap 4.

* ``opt_checkbox_switch`` - Use switches for checkboxes (if custom controls).

* ``opt_size`` - Apply size to form elements. E.g. ``Bootstrap4.SIZE_SMALL``

* ``opt_disabled_plaintext`` - Render disabled fields as plain text.

* ``opt_feedback_tooltips`` - Whether to render feedback in tooltips.

* ``opt_tag_feedback`` - Tag to be used for feedback. Default: div.
