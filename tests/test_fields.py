import pytest
import dataclasses
import typing

from dataclasses_avroschema import fields


INMUTABLE_TYPES_AND_DEFAULTS = (
    (str, "test"),
    (int, 1),
    (bool, True),
    (float, 10.4),
)

LIST_TYPE_AND_ITEMS_TYPE = (
    (str, "string"),
    (int, "int"),
    (bool, "boolean"),
    (float, "float"),
)


def test_invalid_type_field():
    python_type = typing.Set
    name = "test_field"
    msg = f"Invalid Type for field {name}. Accepted types are list, tuple or dict"

    with pytest.raises(ValueError, match=msg):
        fields.Field(name, python_type, dataclasses.MISSING)


@pytest.mark.parametrize("inmutable_type", fields.PYTHON_INMUTABLE_TYPES)
def test_inmutable_types(inmutable_type):
    name = "a_field"
    field = fields.Field(name, inmutable_type, dataclasses.MISSING)
    avro_type = fields.PYTHON_TYPE_TO_AVRO[inmutable_type]

    assert {"name": name, "type": avro_type} == field.to_dict()


@pytest.mark.parametrize("inmutable_type", fields.PYTHON_INMUTABLE_TYPES)
def test_inmutable_types_with_default_value_none(inmutable_type):
    name = "a_field"
    field = fields.Field(name, inmutable_type, None)
    avro_type = [fields.NULL, fields.PYTHON_TYPE_TO_AVRO[inmutable_type]]

    assert {"name": name, "type": avro_type, "default": fields.NULL} == field.to_dict()


@pytest.mark.parametrize("inmutable_type,default", INMUTABLE_TYPES_AND_DEFAULTS)
def test_inmutable_types_with_default_value(inmutable_type, default):
    name = "a_field"
    field = fields.Field(name, inmutable_type, default)
    avro_type = [fields.PYTHON_TYPE_TO_AVRO[inmutable_type], fields.NULL]

    assert {"name": name, "type": avro_type, "default": default} == field.to_dict()


def test_tuple_type():
    """
    When the type is Tuple, the Avro field type should be enum
    with the symbols attribute present.
    """
    name = "an_enum_field"
    default = ("BLUE", "YELOW", "RED",)
    python_type = typing.Tuple
    field = fields.Field(name, python_type, default)

    assert {"name": name, "type": "enum", "symbols": list(default)} == field.to_dict()


@pytest.mark.parametrize("python_primitive_type,python_type_str", LIST_TYPE_AND_ITEMS_TYPE)
def test_list_type(python_primitive_type, python_type_str):
    """
    When the type is List, the Avro field type should be array
    with the items attribute present.
    """
    name = "an_array_field"
    python_type = typing.List[python_primitive_type]
    field = fields.Field(name, python_type, dataclasses.MISSING)

    assert {"name": name, "type": "array", "items": python_type_str} == field.to_dict()


def test_list_type_default_value():
    """
    When the type is List, the Avro field type should be array
    with the items attribute present.
    """
    name = "an_array_field"
    python_type = typing.List[int]

    field = fields.Field(name, python_type, None)
    assert {"name": name, "type": "array", "items": "int", "default": []} == field.to_dict()

    field = fields.Field(name, python_type, [1, 2])
    assert {"name": name, "type": "array", "items": "int", "default": [1, 2]} == field.to_dict()


@pytest.mark.parametrize("python_primitive_type,python_type_str", LIST_TYPE_AND_ITEMS_TYPE)
def test_dict_type(python_primitive_type, python_type_str):
    """
    When the type is Dict, the Avro field type should be map
    with the values attribute present. The keys are always string type.
    """
    name = "a_map_field"
    python_type = typing.Dict[str, python_primitive_type]
    field = fields.Field(name, python_type, dataclasses.MISSING)

    assert {"name": name, "type": "map", "values": python_type_str} == field.to_dict()
