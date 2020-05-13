from typing import Type

import pytest
from pytest_djangoapp import configure_djangoapp_plugin

from siteforms.composers.base import FORM, ALL_FIELDS
from siteforms.toolbox import ModelForm

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
                'other': ALL_FIELDS,
            }
        },
    )


@pytest.fixture
def model_form():

    def model_form_(*, model, composer, options = None, **kwargs) -> Type[ModelForm]:

        Form = type('DynForm', (ModelForm,), dict(
            Composer=type('Composer', (composer,), options or {}),
            Meta=type('Meta', (object,), dict(model=model, fields='__all__')),
            **kwargs
        ))

        return Form

    return model_form_


@pytest.fixture
def form_fixture_match(datafix_read):

    def form_fixture_match_(form, fname):
        rendered = str(form).strip()
        assert rendered == datafix_read(fname).strip()

    return form_fixture_match_
