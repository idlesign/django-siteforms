from typing import Type, Union, List

import pytest
from pytest_djangoapp import configure_djangoapp_plugin

from siteforms.composers.base import FORM, ALL_FIELDS
from siteforms.toolbox import ModelForm, Form

pytest_plugins = configure_djangoapp_plugin()


@pytest.fixture
def layout():
    return dict(
        groups={
            'basic': 'MYBasicGroup',
            'other': 'somethingmore',
        },
        layout={
            FORM: {
                'basic': [
                    ['fchar', 'fbool'],
                    'ftext',
                ],
                '_': ['ffile'],
                'other': ALL_FIELDS,
            }
        },
    )


@pytest.fixture
def form():

    from siteforms.composers.base import FormComposer

    def form_(
            *,
            composer=None,
            model=None,
            options: dict = None,
            fields: Union[List[str], str] = None,
            model_meta: dict = None,
            **kwargs
    ) -> Union[Type[Form], Type[ModelForm]]:

        if composer is None:
            composer = FormComposer

        form_attrs = dict(
            Composer=type('Composer', (composer,), options or {}),
            **kwargs
        )

        form_cls = Form

        if model:
            model_meta = {
                'model': model,
                'fields': fields or '__all__',
                **(model_meta or {}),
            }
            form_attrs['Meta'] = type('Meta', (object,), model_meta)
            form_cls = ModelForm

        return type('DynForm', (form_cls,), form_attrs)

    return form_


@pytest.fixture
def form_html(form):

    def form_html_(options=None, *, composer=None, model=None, **kwargs):
        frm = form(model=model, composer=composer, options=options)(**kwargs)
        return f'{frm}'

    return form_html_


@pytest.fixture
def form_fixture_match(datafix_read):

    def form_fixture_match_(form, fname):
        rendered = str(form).strip()
        assert rendered == datafix_read(fname).strip()

    return form_fixture_match_
