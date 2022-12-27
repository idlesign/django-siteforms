from siteforms.composers.base import FormComposer
from siteforms.composers.bootstrap4 import Bootstrap4, FORM, ALL_FIELDS
from siteforms.composers.bootstrap5 import Bootstrap5
from siteforms.toolbox import ModelForm, Form, fields
from .models import Article, Author
from .utils import render_themed


THEMES = {
    'none': ('No CSS', (FormComposer,)),
    'bootstrap4': ('Bootstrap 4', (Bootstrap4,)),
    'bootstrap5': ('Bootstrap 5', (Bootstrap5,)),
}


class SubFormBase(Form):

    first = fields.CharField(label='some', help_text='some help')
    second = fields.ChoiceField(label='variants', choices={'1': 'one', '2': 'two'}.items())


class ArticleFormMeta:

    model = Article
    fields = '__all__'


class AuthorFormMeta:

    model = Author
    fields = '__all__'


opts = {
    'layout': (
        {
            FORM: {
                'basic': [
                    ['title', ['date_created', 'author', 'status']],
                    'contents',
                ],
                '_': ['dummy'],
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
    'opt_title_label': (True, False),
    'opt_title_help': (True, False),

    # bs4
    'opt_columns': (True, False),
    'opt_custom_controls': (True, False),
    'opt_checkbox_switch': (True, False),
    'opt_feedback_tooltips': (True, False),
    'opt_disabled_plaintext': (True, False),

    # bs5
    'opt_labels_floating': (True, False),
    'opt_feedback_valid': (True, False),
}


def handle_opts(request, composer_options):
    values = {}

    for opt, (on, off) in sorted(opts.items(), key=lambda item: item[0]):
        val = request.GET.get(f'do_{opt}', '0')

        casted = on if val == '1' else off
        if casted is not None:
            composer_options[opt] = casted

        values[f'do_{opt}'] = val

    return values


def themed(request, theme):
    return index(request, theme)


def index(request, theme='none'):

    article = Article.objects.get(pk=1)

    title, composer = THEMES.get(theme)

    composer_options = dict(
        opt_size='sm',

        attrs={
            'contents': {'rows': 2},
            FORM: {'novalidate': ''},
        },
        groups={
            'basic': 'Basic attributes',
            'other': 'Other fields',
        },
    )

    option_values = handle_opts(request, composer_options)

    SubForm1 = type('SubForm', (SubFormBase,), dict(
        Composer=type('Composer', composer, {
            'opt_render_labels': False,
            'opt_placeholder_label': True,
            'layout': {
                FORM: {'_': ALL_FIELDS}
            }
        }),
    ))

    Form = type('ArticleForm', (ModelForm,), dict(
        Composer=type('Composer', composer, composer_options),
        Meta=ArticleFormMeta,
        subforms={'formsub1': SubForm1},
        readonly_fields={'email'},
        disabled_fields={'dummy'},
        hidden_fields={'to_hide'},
    ))

    form1: ModelForm = Form(
        request=request,
        src='POST',
        instance=article,
    )

    class FilterForm(ModelForm):

        Composer = type(
            'Composer', composer,
            {**composer_options, 'opt_form_inline': True, 'opt_render_labels': True}
        )

        class Meta:
            model = Article
            fields = ['title', 'approved', 'status']

    form_filtering1 = FilterForm(request=request, src='GET', id='flt')

    qs = Article.objects.all()
    listing = form_filtering1.filtering_apply(qs)

    if form1.is_valid():
        form1.add_error(None, 'This is a non-field error 1.')
        form1.add_error(None, 'And this one is a non-field error 2.')

    context = {
        'theme': theme,
        'title': title,
        'nav_items': {alias: descr[0] for alias, descr in THEMES.items()},
        'url': request.build_absolute_uri(),
        'opts': option_values,
        'form1': form1,
        'form_filtering1': form_filtering1,
        'listing': listing,
    }

    return render_themed(request, 'index', context)
