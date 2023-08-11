import pytest
import cexprtk


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


@pytest.mark.env
def test_cexprtk_wrapper():
    """
    Test cexprtk python wrapper is working as expected in our environment
    """

    result = cexprtk.evaluate_expression("(A+B)*C", {"A": 5, "B": 5, "C": 23})
    assert isinstance(result, float)

    from numpy.testing import assert_almost_equal
    assert_almost_equal(result, 230.0)


@pytest.mark.env
@pytest.mark.parametrize(
        "expr_string, dependents, expected",
        [
            (
                "(A+B)*C",
                {"A": 5, "B": 5},
                pytest.raises(cexprtk._exceptions.ParseException)
            ),
            (
                "(A+B)*C",
                {"A": 5, "B": "hello"},
                pytest.raises(TypeError)
            ),
            (
                "",
                {"A": 5, "B": 5},
                pytest.raises(cexprtk._exceptions.ParseException)
            ),
        ],
)
def test_cexprtk_throw(expr_string, dependents, expected):
    """
    Test cexprtk wrapper throws appropriate errors when expression string
    is not syntactically correct
    """

    with expected:
        cexprtk.evaluate_expression(expr_string, dependents)


@pytest.fixture(scope="module", params=retrieve_valid_map_files())
def retrieve_expr_and_dependents(request):
    """
    Fixture to provide all expression string and dependents pairing in
    each json mapping file
    All dependents are given a random float value between 1.0 and 20.0
    for evaluations sake
    """
    from numpy import random, round
    import json

    expr_array = list()
    json_globals, full_data = dict(), dict()
    with open(request.param[0]) as map_file:  # get mapping json
        full_data = json.load(map_file)
    with open(request.param[1]) as globals_file:  # get globals json
        json_globals = json.load(globals_file)

    # Awful hack.. change later
    if not full_data:
        return []
    full_data = json.dumps(list(full_data.values()))

    temp_map_entries = {
        entry['EXPR']: dict(
            zip(
                entry['PARAMETERS'].keys(),
                round(
                    random.uniform(
                        1.0, 20.0, size=(len(entry['PARAMETERS'].keys()))
                    ), decimals=3
                )
            )
        )
        for entry in json.loads(full_data)
        if 'EXPR' in entry
    }

    for expr, dependents in temp_map_entries.items():
        dependents.update(
                {
                    key: val
                    for key, val in json_globals.items()
                    if key in expr
                }
        )

    expr_array.append(temp_map_entries)

    return expr_array


@pytest.mark.mappings
def test_json_expr_strings_valid(retrieve_expr_and_dependents):
    """
    Test the expression and dependents pairings in the json mapping files
    are valid and evaluate to sensible values
    """

    for mapping_expr_dict in retrieve_expr_and_dependents:
        for expr, dependents in mapping_expr_dict.items():
            st = cexprtk.Symbol_Table(dependents, add_constants=True)
            result = cexprtk.Expression(expr, st)
            assert isinstance(result.value(), float), \
                f"""
                Evaluated expression string failed and did not
                return a valid float type\n
                Issues with EXPR: {expr} and DEP: {dependents}
                """
