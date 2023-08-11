"""Tests to collect valid mapping and schema pairs,
as well as validating the json is accurate and conforms to schema"""
import pytest
import jsonschema
import json


def retrieve_valid_map_schema():
    """
    Retrieve List of (JSON, top-level schema) filenames
    Only existing files are added and JSON->schema matching done
    currently only using top-level JSON schema but could be modified
    to use a separate JSON schema for each mapping IDS
    All added mappings and schemas should be retrieved from the directory
    """
    from pathlib import Path
    ids_dirs = [
            dird.name
            for dird in Path('./mappings/').iterdir()
            if dird.is_dir()
    ]
    map_schema_list = [
            (
                Path(f'mappings/{dir}/mappings.json').resolve(),
                Path('schemas/toplevel.schema.json').resolve()
            )
            for dir in ids_dirs
            if Path(f'mappings/{dir}/mappings.json').resolve().exists() and
            Path('schemas/toplevel.schema.json').resolve().exists()
    ]
    return map_schema_list


def retrieve_valid_globals():
    """
    Retrieve List of globals.json for each mapping IDS present
    Only existing files are added, currently the presence of a globals.json
    is not enforced but will be in the future
    """

    from pathlib import Path
    ids_dirs = [
            dird.name
            for dird in Path('./mappings/').iterdir()
            if dird.is_dir()
    ]
    map_globals_list = [
            Path(f'mappings/{dir}/globals.json').resolve()
            for dir in ids_dirs
            if Path(f'mappings/{dir}/globals.json').resolve().exists()
    ]
    return map_globals_list


@pytest.mark.mappings
@pytest.mark.parametrize("map_globals", retrieve_valid_globals())
def test_valid_globals(map_globals):
    """
    Validate associated globals for each IDS is valid JSON
    """
    with open(map_globals) as globals_file:
        json.load(globals_file)


@pytest.mark.mappings
@pytest.mark.parametrize("map_schema", retrieve_valid_map_schema())
def test_valid_structure(map_schema):
    """
    Validate MAST-U mappings against the relevant schema
    """
    with open(map_schema[0]) as map_file, open(map_schema[1]) as schema_file:
        jsonschema.validate(
                instance=json.load(map_file), schema=json.load(schema_file)
        )
