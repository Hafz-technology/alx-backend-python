#!/usr/bin/env python3
"""
Unit test suite for the `client` module.
"""
import unittest
from parameterized import parameterized
from client import GithubOrgClient
from typing import Dict
from unittest.mock import patch, Mock


class TestGithubOrgClient(unittest.TestCase):
    """
    Defines test cases for the `GithubOrgClient` class.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, mock_get_json: Mock) -> None:
        """
        Tests that `GithubOrgClient.org` returns the correct value
        and `get_json` is called once with the correct URL.
        """
        # Define a test payload for the mock
        test_payload = {"name": org_name, "repos_url": "http://example.com"}
        mock_get_json.return_value = test_payload

        # Instantiate the client
        client = GithubOrgClient(org_name)

        # Call the .org property
        result = client.org

        # Define the expected URL
        expected_url = f"https://api.github.com/orgs/{org_name}"

        # Assert get_json was called once with the correct URL
        mock_get_json.assert_called_once_with(expected_url)

        # Assert the result is the expected payload
        self.assertEqual(result, test_payload)
