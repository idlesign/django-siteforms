# Multiple forms in one view

Use a distinct prefix for each form. The prefix separates field names and becomes the default
submit marker, so only the submitted form is bound.

```python title="accounts/views.py"
from django.shortcuts import redirect, render

from .forms import PreferencesForm, ProfileForm


def account_settings(request):
    profile_form = ProfileForm(
        request=request,
        src='POST',
        prefix='profile',
        instance=request.user.profile,
    )
    preferences_form = PreferencesForm(
        request=request,
        src='POST',
        prefix='preferences',
        instance=request.user.preferences,
    )

    if profile_form.is_submitted and profile_form.is_valid():
        profile_form.save()
        return redirect('account-settings')

    if preferences_form.is_submitted and preferences_form.is_valid():
        preferences_form.save()
        return redirect('account-settings')

    return render(request, 'accounts/settings.html', {
        'preferences_form': preferences_form,
        'profile_form': profile_form,
    })
```

Render both forms normally:

```django title="accounts/templates/accounts/settings.html"
<section>
  <h2>Profile</h2>
  {{ profile_form }}
</section>

<section>
  <h2>Preferences</h2>
  {{ preferences_form }}
</section>
```

Each form generates its own `<form>` element and submit button. The profile button submits
`__submit=profile`, while the preferences button submits `__submit=preferences`. siteforms compares
that value with the form's `submit_marker` and exposes the result through `is_submitted`; view code
does not need to inspect `request.POST` itself.

Do not use only `id` to separate forms. It changes HTML IDs, not submitted field names.
