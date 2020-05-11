import pytest
from pytest_djangoapp import configure_djangoapp_plugin


pytest_plugins = configure_djangoapp_plugin()


@pytest.fixture
def form_fixture_match(datafix_read):

    def form_fixture_match_(form, fname):
        rendered = str(form).strip()
        assert rendered == datafix_read(fname).strip()

    return form_fixture_match_
