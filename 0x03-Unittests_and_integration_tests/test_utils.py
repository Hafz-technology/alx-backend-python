#!/usr/bin/env python3
"""
Unit test suite for the `utils` module.
"""
import unittest
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize
from typing import Mapping, Sequence, Any, Dict
from unittest.mock import patch, Mock


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

    @parameterized.expand([
        ({}, ("a",), 'a'),
        ({"a": 1}, ("a", "b"), 'b'),
    ])
    def test_access_nested_map_exception(self,
                                       nested_map: Mapping,
                                       path: Sequence,
                                       expected_msg: str) -> None:
        """
        Tests that `access_nested_map` raises a KeyError with the
        expected message for invalid paths.
        """
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        self.assertEqual(str(cm.exception), f"'{expected_msg}'")


class TestGetJson(unittest.TestCase):
    """
    Defines test cases for the `get_json` utility function.
    """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self,
                    test_url: str,
                    test_payload: Dict,
                    mock_get: Mock) -> None:
        """
        Tests that `get_json` returns the expected JSON payload
        by mocking the `requests.get` call.
        """
        # Configure the mock to return a response object with a json method
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        # Call the function
        result = get_json(test_url)

        # Assert that requests.get was called once with the correct URL
        mock_get.assert_called_once_with(test_url)

        # Assert that the result is the expected payload
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """
    Defines test cases for the `memoize` decorator.
    """

    def test_memoize(self) -> None:
        """
        Tests that `memoize` caches the result of a method
        and the underlying method is only called once.
        """
        class TestClass:
            """A test class for memoization."""

            def a_method(self) -> int:
                """A method to be called."""
                return 42

            @memoize
            def a_property(self) -> int:
                """A memoized property."""
                return self.a_method()

        # Patch the `a_method` on the TestClass
        with patch.object(TestClass,
                          'a_method',
                          return_value=42) as mock_a_method:
            test_obj = TestClass()

            # Call the memoized property twice
            result1 = test_obj.a_property
            result2 = test_obj.a_property

            # Check that the results are correct
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)

            # Check that the underlying method was only called once
            mock_a_method.assert_called_once()
