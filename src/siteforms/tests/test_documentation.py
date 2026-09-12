import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from siteforms.composers.base import FormComposer
from siteforms.toolbox import Form, fields


class AccountForm(Form):

    email = fields.EmailField()

    class Composer(FormComposer):
        pass


class UploadForm(Form):

    attachment = fields.FileField(required=False)

    class Composer(FormComposer):
        pass


def test_documented_multiple_forms_workflow(request_post):
    request = request_post(data={
        '__submit': 'profile',
        'profile-email': 'reader@example.com',
    })
    profile_form = AccountForm(
        request=request,
        src='POST',
        prefix='profile',
        id='profile-form',
        target_url='/account/',
    )
    password_form = AccountForm(
        request=request,
        src='POST',
        prefix='password',
    )

    assert profile_form.is_submitted
    assert not password_form.is_submitted
    assert profile_form.is_valid()

    rendered = str(profile_form)
    assert '<form ' in rendered
    assert 'method="POST"' in rendered
    assert 'action="/account/"' in rendered
    assert 'id="profile-form"' in rendered
    assert 'name="profile-email"' in rendered
    assert 'name="__submit" value="profile"' in rendered


def test_documented_form_wrapper_options():
    wrapped = str(UploadForm(target_url='/upload/'))
    assert '<form ' in wrapped
    assert 'method="POST"' in wrapped
    assert 'action="/upload/"' in wrapped
    assert 'enctype="multipart/form-data"' in wrapped

    embedded = str(UploadForm(render_form_tag=False))
    assert '<form ' not in embedded
    assert 'name="attachment"' in embedded


def test_internal_documentation_links_exist():
    project_root = Path(__file__).resolve().parents[3]
    sources = [project_root / 'README.md', *sorted((project_root / 'docs').rglob('*.md'))]
    link_pattern = re.compile(r'!?\[[^]]*]\(([^)\s]+)')

    broken = []
    for source in sources:
        in_fence = False
        for line_number, line in enumerate(source.read_text().splitlines(), start=1):
            if line.lstrip().startswith('```'):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            for match in link_pattern.finditer(line):
                target = match.group(1)
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue

                linked_path = (source.parent / unquote(parsed.path)).resolve()
                if not linked_path.exists():
                    broken.append(f'{source.relative_to(project_root)}:{line_number}: {target}')

    assert not broken, 'Broken documentation links:\n' + '\n'.join(broken)
