"""Tests to ensure testing environment for
inja templating library works as expected and catches syntax errors"""
import pytest
import json


@pytest.mark.env
def test_cython_include():
    """
    Test cython global read and include
    call test_cython and assure type can be cast to float
    and the value equals the expected value
    """

    from inja_test import py_test_cython
    var_cython = py_test_cython()
    assert isinstance(var_cython, float)
    assert var_cython == 42.5


@pytest.mark.env
@pytest.mark.parametrize(
        "test_string, expected",
        [
            (
                "/magnetics/pfcoil/{{indices.1/test",
                pytest.raises(RuntimeError)
            ),
            (
                "/magnetics/pfcoil/{{unknown}}/test",
                pytest.raises(RuntimeError)
            ),
        ],
)
def test_template_syntax_fail(test_string, expected):
    """
    Test inja templating library
    Verify that the templating library will raise an exception if
    incorrect type or syntax errors occur in the template string
    """

    from inja_test import py_test_render
    with expected:
        py_test_render(test_string)


def retrieve_valid_map_files():
    """
    Fixture of paths to the mapping files
    Retrieve list of valid JSON mappings files to be used in other tests
    """

    from pathlib import Path
    ids_dirs = [
            dird.name
            for dird in Path('./mappings/').iterdir()
            if dird.is_dir()
    ]

    mappings_globals_list = [
        (
            Path(f'mappings/{dir}/mappings.json').resolve(),
            Path(f'mappings/{dir}/globals.json').resolve(),
        )
        for dir in ids_dirs
        if Path(f'mappings/{dir}/mappings.json').resolve().exists() and
        Path(f'mappings/{dir}/globals.json').resolve().exists()

    ]

    return mappings_globals_list


@pytest.fixture(params=retrieve_valid_map_files())
def get_keys_and_globals(request):
    """
    Fixture of JSON keys and globals
    Retrieve JSON keys and globals from valid mapping files
    for use in templating validation
    """

    all_keys = list()

    json_globals, full_data = dict(), dict()
    with open(request.param[0]) as map_file:  # get mapping json
        full_data = json.load(map_file)
    with open(request.param[1]) as globals_file:  # get globals json
        json_globals = json.load(globals_file)

    if not json_globals:
        return all_keys  # Check globals not empty, return empty all_keys

    # hack to encode/decode json to python objects properly
    full_data = json.dumps(list(full_data.values()))

    templated_attrs = ["VALUE", "EXPR", "OFFSET", "SCALAR"]
    template_key_list = []
    for entry in json.loads(full_data):
        template_key_list += [
                entry[key] for key in templated_attrs if key in entry
        ]

    template_key_list = [
        element for element in template_key_list
        if isinstance(element, str)
        and ('{{' in element or '}}' in element)
    ]

    if not template_key_list:
        return all_keys  # Empty keys check, return empty all_keys

    # pairs of globals and template keys
    all_keys.append((json.dumps(json_globals), template_key_list))

    # AJPFIX: change to yield/generator expression when jsons grow
    return all_keys


@pytest.mark.mappings
def test_templating_in_json(get_keys_and_globals):
    """
    Test templating output
    Loop through the JSON mappings and their keys and validate the
    templating output will be successful within the plugin
    """

    # AJPFIX: unnecessary looping
    for temp_globals, temp_key_array in get_keys_and_globals:
        for temp_key in temp_key_array:
            assert isinstance(temp_key, str)
            from numpy.testing import assert_equal
            assert_equal(temp_key.count('{{'), temp_key.count('}}'))

            from inja_test import py_test_render_wglobals
            replaced_str = str(py_test_render_wglobals(temp_globals, temp_key))
            assert isinstance(replaced_str, str)
