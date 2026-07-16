# -*- coding: utf-8 -*-
from epint.modules.search.find_closest import dict_key_search, find_closest_match


def test_exact_case_insensitive_match_wins_over_fuzzy():
    result = find_closest_match("MCP_DATA", ["mcp_data", "mcpdata_export"])
    assert result == "mcp_data"


def test_fuzzy_match_above_threshold():
    result = find_closest_match(
        "mcpData", ["mcp_data", "unrelated_thing"], threshold=0.6
    )
    assert result == "mcp_data"


def test_no_match_below_threshold_returns_none():
    assert (
        find_closest_match("zzz", ["mcp_data", "offer_create"], threshold=0.8) is None
    )


def test_empty_inputs_return_none():
    assert find_closest_match("", ["a", "b"]) is None
    assert find_closest_match("a", []) is None


def test_dict_key_search_exact_case_insensitive_pop():
    d = {"Debug": True, "other": 1}
    result = dict_key_search(["debug"], d)
    assert result is True
    assert "Debug" not in d
    assert d == {"other": 1}


def test_dict_key_search_fuzzy_fallback():
    # "regionCod" tam eşleşmiyor (case-insensitive dahi), fuzzy matching devreye girer.
    d = {"regionCod": "TR1"}
    result = dict_key_search(["regionCode"], d)
    assert result == "TR1"
    assert d == {}


def test_dict_key_search_no_match_returns_none_and_leaves_dict_untouched():
    d = {"foo": 1}
    result = dict_key_search(["debug"], d)
    assert result is None
    assert d == {"foo": 1}
