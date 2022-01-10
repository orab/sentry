import inspect
from typing import Any, Optional, Union, _TypedDictMeta, get_args, get_origin, get_type_hints

from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import build_array_type, build_basic_type, is_basic_type
from drf_spectacular.plumbing import resolve_type_hint

# from drf_spectacular.plumbing import get_doc, safe_ref

PUBLIC_SERIALIZERS = set()
# https://www.python.org/dev/peps/pep-0655/


# TODO: map things in registry
def is_optional(field) -> bool:
    # https://stackoverflow.com/a/58841311
    return get_origin(field) is Union and type(None) in get_args(field)


def map_field_from_type(t: type) -> Any:
    if type(t) == _TypedDictMeta:
        return map_typedict(t), True

    if is_basic_type(t):
        schema = build_basic_type(t)
        if schema is None:
            return None
        return schema, True

    if get_origin(t) is list:
        field, required = map_field_from_type(t.__args__[0])
        return build_array_type(field), True

    if is_optional(t):
        return map_field_from_type(get_args(t)[0])[0], False
    raise Exception("couldn't find a type!")


# Private attributes?
def map_typedict(t, excluded_fields=None):
    if not excluded_fields:
        excluded_fields = []
    # TODO: add descriptions from __doc__
    # TODO: register nested TypedDicts as components
    properties = {}
    required = set()
    for k, v in get_type_hints(t).items():
        if k in excluded_fields:
            continue
        field, field_required = map_field_from_type(v)
        properties[k] = field
        if field_required:
            required.add(k)
    # return build_object_type(properties, required=set(), description="")
    description = t.__doc__ or ""
    return {
        "type": "object",
        "properties": properties,
        "required": list(required),
        "description": description,
    }


def get_class(obj) -> type:
    return obj if inspect.isclass(obj) else obj.__class__


class SentryResponseSerializerExtension(OpenApiSerializerExtension):
    priority = 0
    target_class = "sentry.api.serializers.base.Serializer"
    match_subclasses = True

    def get_name(self) -> Optional[str]:
        return self.target.__name__

    @classmethod
    def _matches(cls, target) -> bool:
        if isinstance(cls.target_class, str):
            cls._load_class()

        if cls.target_class is None:
            return False  # app not installed
        elif cls.match_subclasses:
            return (
                issubclass(get_class(target), cls.target_class)
                and f"{target.__module__}.{target.__name__}" in PUBLIC_SERIALIZERS
            )
        else:
            return get_class(target) == cls.target_class

    def map_serializer(self, auto_schema, direction):
        serializer_signature = inspect.signature(self.target.serialize)
        return resolve_type_hint(serializer_signature.return_annotation)


class SentryInlineResponseSerializerExtension(OpenApiSerializerExtension):
    priority = 0
    target_class = "sentry.apidocs.schemaserializer.RawSchema"
    match_subclasses = True

    def get_name(self) -> Optional[str]:
        return self.target.__name__

    @classmethod
    def _matches(cls, target) -> bool:
        if isinstance(cls.target_class, str):
            cls._load_class()

        if cls.target_class is None:
            return False  # app not installed
        elif cls.match_subclasses:
            return issubclass(get_class(target), cls.target_class)
        else:
            return get_class(target) == cls.target_class

    def map_serializer(self, auto_schema, direction):
        return resolve_type_hint(self.target.typeSchema)


# def inline_list_serializer(serializer):
#     from sentry.apidocs.decorators import mark_serializer_public

#     sig = inspect.signature(serializer.serialize)
#     serializer_return_annotation = sig.return_annotation

#     @mark_serializer_public
#     class ListResponseSerializer(Serializer):
#         def serialize(self) -> List[serializer_return_annotation]:
#             pass

#     return ListResponseSerializer


class RawSchema:
    def __init__(self, type):
        self.typeSchema = type


def inline_sentry_response_serializer(name, t):
    serializer_class = type(name, (RawSchema,), {"typeSchema": t})
    return serializer_class


# class PrimitiveType:
#     pass


# class PublicSchemaResponseSerializerExtension(OpenApiSerializerExtension):
#     priority = 0
#     target_class = "sentry.apidocs.schemaserializer.PrimitiveType"
#     match_subclasses = True

#     def get_name(self) -> Optional[str]:
#         return self.target.__name__

#     @classmethod
#     def _matches(cls, target) -> bool:
#         if isinstance(cls.target_class, str):
#             cls._load_class()

#         if cls.target_class is None:
#             return False  # app not installed
#         elif cls.match_subclasses:
#             return (
#                 issubclass(get_class(target), cls.target_class)
#                 and f"{target.__module__}.{target.__name__}" in PUBLIC_SERIALIZERS
#             )
#         else:
#             return get_class(target) == cls.target_class

#     def map_serializer(self, auto_schema, direction):
#         return map_serializer(self.target)


# TODO: create this for our types
# def inline_serializer(name: str, fields: Dict[str, Field], **kwargs) -> Serializer:
#     """
#     A helper function to create an inline serializer. Primary use is with
#     :func:`@extend_schema <.extend_schema>`, where one needs an implicit one-off
#     serializer that is not reflected in an actual class.

#     :param name: name of the
#     :param fields: dict with field names as keys and serializer fields as values
#     :param kwargs: optional kwargs for serializer initialization
#     """
#     serializer_class = type(name, (Serializer,), fields)
#     return serializer_class(**kwargs)
