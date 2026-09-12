# Multiple forms in one view

Use a distinct prefix for each form. The prefix separates field names and becomes the default
submit marker, so only the submitted form is bound.

```python title="accounts/views.py"
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import redirect, render

from .forms import ProfileForm


def account_settings(request):
    profile_form = ProfileForm(
        request=request,
        src='POST',
        prefix='profile',
        instance=request.user.profile,
    )
    password_form = SetPasswordForm(
        user=request.user,
        data=request.POST if request.method == 'POST' else None,
        prefix='password',
    )

    if profile_form.is_submitted and profile_form.is_valid():
        profile_form.save()
        return redirect('account-settings')

    password_submitted = request.POST.get('__submit') == 'password'
    if password_submitted and password_form.is_valid():
        password_form.save()
        return redirect('account-settings')

    return render(request, 'accounts/settings.html', {
        'password_form': password_form,
        'profile_form': profile_form,
    })
```

This example combines a siteforms form with Django's `SetPasswordForm`. The ordinary Django form
does not generate a siteforms marker, so its button is supplied explicitly:

```django title="accounts/templates/accounts/settings.html"
<section>
  <h2>Profile</h2>
  {{ profile_form }}
</section>

<section>
  <h2>Password</h2>
  <form method="post">
    {% csrf_token %}
    {{ password_form.as_div }}
    <button type="submit" name="__submit" value="password">
      Change password
    </button>
  </form>
</section>
```

If both forms inherit from siteforms classes, construct both with `request`, `src='POST'`, and
different prefixes, then use each form's `is_submitted` flag. Each will render its own complete
`<form>` element and submit button.

Do not use only `id` to separate forms. It changes HTML IDs, not submitted field names.
