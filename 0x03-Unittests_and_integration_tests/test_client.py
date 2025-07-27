#!/usr/bin/env python3
"""
Unit and integration tests for GithubOrgClient.
"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """
    Tests for the GithubOrgClient class.
    """
    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, expected_payload: dict, mock_get_json: patch) -> None:
        """
        Test that GithubOrgClient.org returns the correct value.
        Uses @patch as a decorator to mock get_json.
        """
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected_payload)
        mock_get_json.assert_called_once_with(
            GithubOrgClient.ORG_URL.format(org=org_name)
        )

    def test_public_repos_url(self) -> None:
        """
        Test that _public_repos_url returns the expected URL
        based on a mocked org payload.
        """
        expected_repos_url = "https://api.github.com/orgs/testorg/repos"
        # Patch GithubOrgClient.org as a property
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            # Set the return value of the mocked org property
            mock_org.return_value = {"repos_url": expected_repos_url}

            # Create an instance of GithubOrgClient
            client = GithubOrgClient("testorg")

            # Assert that _public_repos_url returns the expected value
            self.assertEqual(client._public_repos_url, expected_repos_url)

            # Assert that the org property was called exactly once
            mock_org.assert_called_once()


if __name__ == '__main__':
    unittest.main()
