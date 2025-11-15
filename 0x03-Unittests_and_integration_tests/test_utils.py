#!/usr/bin/env python3
"""
Unit tests for the utils.py module.
"""
import unittest
from parameterized import parameterized
from typing import Mapping, Sequence, Any
from utils import access_nested_map


class TestAccessNestedMap(unittest.TestCase):
    """
    Test class for the access_nested_map function.
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map: Mapping,
                             path: Sequence,
                             expected: Any) -> None:
        """
        Test that access_nested_map returns the correct value for given paths.
        The body is a single line as requested.
        """
        # Test that the function's output equals the expected output
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), 'a'),
        ({"a": 1}, ("a", "b"), 'b'),
    ])
    def test_access_nested_map_exception(self, nested_map: Mapping,
                                       path: Sequence,
                                       expected_msg: str) -> None:
        """
        Test that access_nested_map raises KeyError for invalid paths
        and checks the exception message.
        """
        # Use assertRaises as a context manager to catch the KeyError
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        
        # Check that the exception message is the key that caused the error
        # str(KeyError('a')) results in 'a'
        self.assertEqual(str(cm.exception), expected_msg)


if __name__ == '__main__':
    unittest.main()
