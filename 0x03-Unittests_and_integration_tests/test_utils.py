#!/usr/bin/env python3

"""
Unit tests for the utils module functions.
"""


"""
Unit tests for the utils module functions.
"""
import unittest
from parameterized import parameterized
from utils import access_nested_map


# import unittest
# from parameterized import parameterized
# from utils import access_nested_map


# class TestAccessNestedMap(unittest.TestCase):
#     """
#     Tests the access_nested_map function from utils.
#     """

#     @parameterized.expand([
#         ({"a": 1}, ("a",), 1),
#         ({"a": {"b": 2}}, ("a",), {"b": 2}),
#         ({"a": {"b": 2}}, ("a", "b"), 2),
#     ])
#     def test_access_nested_map(self, nested_map, path, expected):
#         """
#         Tests that access_nested_map returns the expected result
#         for various valid inputs.
#         """
#         self.assertEqual(access_nested_map(nested_map, path), expected)



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


