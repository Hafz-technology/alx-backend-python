#!/usr/bin/env python3
"""
Unit test suite for the `client` module.
"""
import unittest
from parameterized import parameterized
from client import GithubOrgClient
from typing import Dict
from unittest.mock import patch, Mock, PropertyMock


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

    def test_public_repos_url(self) -> None:
        """
        Tests that `GithubOrgClient._public_repos_url` returns the
        correct URL based on the mocked `org` property.
        """
        # Define a known payload for the `org` property
        known_payload = {"repos_url": "https://api.github.com/orgs/google/repos"}

        # Patch the `org` property using patch.object and PropertyMock
        with patch.object(GithubOrgClient,
                          'org',
                          new_callable=PropertyMock) as mock_org:
            # Set the return value for the mocked property
            mock_org.return_value = known_payload

            # Instantiate the client
            client = GithubOrgClient("google")

            # Access the `_public_repos_url` property
            repos_url = client._public_repos_url

            # Assert that the repos_url is the one from the payload
            self.assertEqual(repos_url, known_payload["repos_url"])
