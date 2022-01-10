from typing import Iterable, Literal

from .preprocessor import PUBLIC_ENDPOINTS
from .schemaserializer import PUBLIC_SERIALIZERS

http_methods = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]


def declare_public(methods: Iterable[http_methods]):
    def decorate(view_cls):
        PUBLIC_ENDPOINTS[view_cls.__name__] = {
            "callback": view_cls,
            "methods": methods,
        }

        return view_cls

    return decorate


def mark_serializer_public(serializer_cls):
    PUBLIC_SERIALIZERS.add(f"{serializer_cls.__module__}.{serializer_cls.__name__}")
    return serializer_cls
