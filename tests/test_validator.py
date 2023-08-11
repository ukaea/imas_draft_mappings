"""Tests to ensure the environment for jsonschema validation
works and tests as expected"""
import json
import pytest
from jsonschema import validate, exceptions


@pytest.mark.env
def test_json_open():
    """
    Test JSON loader
    Open JSON file, compare object to expected dict and types
    """

    expected = {
        'mappings': {
            'ID': '0001',
            'NUMBER': 42,
            'BALANCE': 26.5,
            'UNIQUE': False
        }
    }

    with open('mappings/mock/test_open.json') as json_file:
        json_open = json.load(json_file)

    mappings = json_open['mappings']

    assert json_open == expected
    assert isinstance(mappings['ID'], str)
    assert isinstance(mappings['NUMBER'], int)
    assert isinstance(mappings['BALANCE'], float)
    assert isinstance(mappings['UNIQUE'], bool)


@pytest.mark.env
def test_json_open_fail():
    """
    Test JSON loader
    Load JSON file with incorrect JSON structure
    and check DecodeError exception is raised
    """

    with pytest.raises(json.decoder.JSONDecodeError):
        with open('mappings/mock/test_open_fail.json') as json_file:
            json.load(json_file)


@pytest.mark.env
def test_json_schema_pass():
    """
    Test jsonschema module
    Run jsonschema validation for expected JSON input corresponding schema
    """

    expected_json = {
        'mappings': {
            'ID': '0001',
            'NUMBER': 42,
            'BALANCE': 26.5,
            'UNIQUE': False
        }
    }

    expected_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "https://example.com/object1635031661.json",
        "title": "Root",
        "type": "object",
        "required": [
            "mappings"
        ],
        "properties": {
            "mappings": {
                "$id": "#root/mappings",
                "title": "Mappings",
                "type": "object",
                "required": [
                    "ID",
                    "NUMBER",
                    "BALANCE",
                    "UNIQUE"
                ],
                "properties": {
                    "ID": {
                        "$id": "#root/mappings/id",
                        "title": "ID",
                        "type": "string",
                        "default": "",
                        "examples": [
                            "0001"
                        ],
                        "pattern": "^.*$"
                    },
                    "NUMBER": {
                        "$id": "#root/mappings/number",
                        "title": "Number",
                        "type": "integer",
                        "examples": [
                            42
                        ],
                        "default": 0
                    },
                    "BALANCE": {
                        "$id": "#root/mappings/balance",
                        "title": "Balance",
                        "type": "number",
                        "examples": [
                            26.5
                        ],
                        "default": 0.0
                    },
                    "UNIQUE": {
                        "$id": "#root/mappings/unique",
                        "title": "Unique",
                        "type": "boolean",
                        "examples": [
                            False
                        ],
                        "default": True
                    }
                }
            }
        }
    }

    validate(instance=expected_json, schema=expected_schema)


@pytest.mark.env
def test_json_schema_fail():
    """
    Test jsonschema module
    Run jsonschema vaidator for JSON and schema incompatibility,
    and raise ValidationError
    """

    expected_json = {
        'mappings': {
            'ID': '0001',
            'NUMBER': 42,
            'UNIQUE': False
        }
    }

    expected_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "https://example.com/object1635031661.json",
        "type": "object",
        "properties": {
            "mappings": {
                "type": "object",
                "required": [
                    "ID",
                    "NUMBER",
                    "BALANCE",
                    "UNIQUE"
                ],
                "properties": {
                    "ID": {
                        "type": "string"
                    },
                    "NUMBER": {
                        "type": "integer"
                    },
                    "BALANCE": {
                        "type": "number"
                    },
                    "UNIQUE": {
                        "type": "boolean"
                    }
                }
            }
        }
    }

    with pytest.raises(exceptions.ValidationError):
        validate(instance=expected_json, schema=expected_schema)


@pytest.mark.env
def test_json_schema_comp():
    """
    Test jsonschema module with file loading
    Load in JSON and corresponding schema and validate with jsonschema
    """

    map_path = 'mappings/mock/mappings.json'
    schema_path = 'schemas/toplevel.schema.json'
    with open(map_path) as map_file, open(schema_path) as schema_file:
        validate(instance=json.load(map_file), schema=json.load(schema_file))
