from uuid import UUID

from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions


def validate_uuid(target: UUID, error_msg: str = "") -> None:
    """
    Raise rest_framework 404 exception with default or custom `error_msg`
    """
    try:
        UUID(target)
    except ValueError:
        raise exceptions.NotFound(_(error_msg)) if error_msg else exceptions.NotFound()
