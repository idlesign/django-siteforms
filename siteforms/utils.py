from typing import Optional, Union

from django.forms import Field

if False:  # pragma: nocover
    from .base import TypeSubform  # noqa


UNSET = set()
"""Value is not set sentinel."""


def merge_dict(src: Optional[dict], dst: Union[dict, str]) -> dict:

    if src is None:
        src = {}

    if isinstance(dst, str):
        # Strings are possible when base layout (e.g. ALL_FIELDS)
        # replaced by user-defined layout.
        return src.copy()

    out = dst.copy()

    for k, v in src.items():
        if isinstance(v, dict):
            v = merge_dict(v, dst.setdefault(k, {}))
        out[k] = v

    return out


def bind_subform(*, subform: 'TypeSubform', field: Field):
    """Initializes field attributes thus linking them to a subform.

    :param subform:
    :param field:

    """
    field.widget.form = subform
    field.form = subform
