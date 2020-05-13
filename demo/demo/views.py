from siteforms.composers.base import FormComposer
from siteforms.composers.bootstrap4 import Bootstrap4, FORM, ALL_FIELDS
from siteforms.toolbox import ModelForm
from .models import Article
from .utils import render_themed


THEMES = {
    'none': ('No CSS', (FormComposer,)),
    'bootstrap4': ('Bootstrap 4', (Bootstrap4,)),
}


class Form1Meta:
    model = Article
    fields = '__all__'


opts = {
    'layout': (
        {
            FORM: {
                'basic': [
                    ['title', 'date_created'],
                    'contents',
                ],
                'other': ALL_FIELDS,
            }
        },
        None,
    ),
    'opt_form_inline': (True, False),
    'opt_render_labels': (True, False),
    'opt_render_help': (True, False),
    'opt_placeholder_label': (True, False),
    'opt_placeholder_help': (True, False),

    # bs4
    'opt_custom_controls': (True, False),
    'opt_checkbox_switch': (True, False),
    'opt_columns': (True, False),
}


def handle_opts(request, composer_options):
    values = {}

    for opt, (on, off) in opts.items():
        val = request.GET.get(f'do_{opt}', '0')

        casted = on if val == '1' else off
        if casted is not None:
            composer_options[opt] = casted

        values[f'do_{opt}'] = val

    return values


def index(request):

    title, composer = THEMES.get(request.theme.strip('_'))

    composer_options = dict(
        opt_size='sm',

        attrs={
            'contents': {'rows': 2},
        },
        groups={
            'basic': 'Basic attributes',
            'other': 'Other fields',
        },
    )

    option_values = handle_opts(request, composer_options)

    Form = type('ArticleForm', (ModelForm,), dict(
        Composer=type('Composer', composer, composer_options),
        Meta=Form1Meta,
        disabled_fields={'dummy'},
        hidden_fields={'to_hide'},
    ))

    form1 = Form(request=request, src='POST')

    if form1.is_valid():
        pass

    context = {
        'title': title,
        'nav_items': {alias: descr[0] for alias, descr in THEMES.items()},
        'url': request.build_absolute_uri(),
        'opts': option_values,
        'form1': form1,
    }

    return render_themed(request, 'index', context)

