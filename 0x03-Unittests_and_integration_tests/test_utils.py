#!/usr/bin/env python3
"""
Unit tests for the utils module functions.
"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json


class TestAccessNestedMap(unittest.TestCase):
    """
    Tests the access_nested_map function from utils.
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """
        Tests that access_nested_map returns the expected result
        for various valid inputs.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_msg):
        """
        Tests that access_nested_map raises a KeyError with the expected message
        for invalid inputs.
        """
        with self.assertRaisesRegex(KeyError, expected_msg):
            access_nested_map(nested_map, path)


class TestGetJson(unittest.TestCase):
    """
    Tests the get_json function from utils.
    """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        """
        Tests that get_json returns the expected result and
        that requests.get is called exactly once with the correct URL.
        """
        # Configure the mock to return a Mock object with a json method
        mock_get.return_value.json.return_value = test_payload

        # Call the function under test
        result = get_json(test_url)

        # Assertions
        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)

