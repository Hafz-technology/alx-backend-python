#!/usr/bin/env python3
"""
Unit test suite for the `utils` module.
"""
import unittest
from parameterized import parameterized
from utils import access_nested_map
from typing import Mapping, Sequence, Any


class TestAccessNestedMap(unittest.TestCase):
    """
    Defines test cases for the `access_nested_map` utility function.
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self,
                             nested_map: Mapping,
                             path: Sequence,
                             expected: Any) -> None:
        """
        Tests that `access_nested_map` correctly retrieves nested values.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)
