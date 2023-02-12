from uuid import UUID

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.exceptions import PermissionDenied

User = get_user_model()


def validate_uuid(target: UUID, error_msg: str = "") -> None:
    """
    Raise rest_framework 404 exception with default or custom `error_msg`
    """
    try:
        UUID(target)
    except ValueError:
        raise exceptions.NotFound(_(error_msg)) if error_msg else exceptions.NotFound()


def compare_users_and_restrict(
    request_user: User, instance_user: User, call_from: str = "serializer"
) -> None:
    """Compare 2 users and raise error if they're not equal. Staff users are omitted.

    Raises:
        serializers.ValidationError: if call_from was "serializer"
        PermissionDenied: if call_from was "view"
    """
    if not request_user.is_staff and request_user != instance_user:
        msg = "You can only change your own data."
        match call_from:
            case "serializer":
                raise serializers.ValidationError(msg)
            case "view":
                raise PermissionDenied(msg)


def validate_two_uuids(uuid_1: UUID, uuid_2: UUID) -> None:
    """Compare 2 uuids and raise error if they're not equal.

    Raises:
        serializers.ValidationError
    """
    if uuid_1 != uuid_2:
        raise serializers.ValidationError()
