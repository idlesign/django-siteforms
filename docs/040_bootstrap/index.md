# Bootstrap composers

`django-siteforms` includes composers for Bootstrap 5 and Bootstrap 4. They generate the classes
and structure expected by the selected Bootstrap major version while retaining the normal
siteforms request, validation, layout, and subform behaviour.

The package does not include Bootstrap CSS or JavaScript. Load those assets in the application's
base template using the installation method recommended by the Bootstrap project.

Choose the composer that matches the assets already used by the application:

- [Bootstrap 5](010_bootstrap5.md) is the recommended default for new integrations;
- [Bootstrap 4](020_bootstrap4.md) remains available for applications using Bootstrap 4 markup.

Both composers are exercised by the project test suite. Do not combine a Bootstrap 4 composer with
Bootstrap 5 assets, or the reverse: several control, validation, spacing, and custom-control
classes differ between the major versions.

For framework-independent configuration, see [Composers](../020_composers/index.md).
