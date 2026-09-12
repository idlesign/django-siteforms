# Troubleshooting

## `is_submitted` stays false

Check all parts of submission detection:

- the form receives both `request` and `src`;
- `src` matches `request.method`, including uppercase spelling;
- the submitted data contains `Composer.opt_submit_name`, normally `__submit`;
- its value matches `form.submit_marker`;
- a custom wrapper reproduces the generated submit button's name and value.

With a prefixed form, the default marker is the prefix rather than `siteform`.

## Invalid fields show no feedback

Composer field feedback is shown for a submitted siteforms form. If data was bound manually without
the expected marker, Django may consider the form bound while `form.is_submitted` remains false.
Prefer request-aware construction or set the correct marker in the submitted data.

## Two forms consume the same values

Give every form a unique Django `prefix`. An HTML `id` does not change field names and cannot
isolate submitted values.

## A field disappeared after changing `layout`

An explicit grouped layout renders only referenced visible fields. Add `ALL_FIELDS` where remaining
fields should be inserted. Also ensure that a field is not referenced twice or misspelled.

## Bootstrap styles are missing

Bootstrap composers generate compatible markup but do not include CSS or JavaScript. Load the same
Bootstrap major version as the selected composer and check custom attributes for classes belonging
to another version.

## A hidden field makes the form invalid

Hidden fields are still submitted and validated. Their errors appear with non-field feedback. Do
not hide a required field unless the request supplies a valid value or the form provides valid
initial data.

## A many-to-many subform reports management-form errors

Do not remove the generated formset management fields. JavaScript that inserts or deletes rows must
follow Django formset conventions and update `TOTAL_FORMS` and the corresponding indexed field
names.

## Related objects remain after invalid validation

A valid foreign-key subform or an extra many-to-many form can create an object while the parent is
being cleaned. Wrap both validation and saving in `transaction.atomic()` and mark the transaction
for rollback when the overall form is invalid. See
[Validation and saving](../025_subforms/050_lifecycle.md).

## The page contains nested `<form>` elements

Top-level siteforms forms render their own wrapper. Pass `render_form_tag=False` when placing one
inside a wrapper supplied by the template. Registered subforms already disable their own wrappers
automatically.
