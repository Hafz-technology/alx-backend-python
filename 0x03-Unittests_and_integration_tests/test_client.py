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
    def test_org(self,
                 org_name: str,
                 expected_payload: dict,
                 mock_get_json: patch) -> None:
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

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: patch) -> None:
        """
        Test GithubOrgClient.public_repos method.
        Mocks get_json and _public_repos_url.
        """
        # Define the payload that mock_get_json will return
        mock_repos_payload = [
            {"name": "alx-backend", "license": {"key": "mit"}},
            {"name": "holberton-web", "license": {"key": "apache-2.0"}},
            {"name": "my-app", "license": None},  # No license
            {"name": "old-project", "license": {"key": "gpl-3.0"}},
        ]
        mock_get_json.return_value = mock_repos_payload

        # Define the expected list of repo names
        expected_repo_names = ["alx-backend", "holberton-web",
                               "my-app", "old-project"]

        # Define the URL that mock_public_repos_url will return
        mock_repos_url = "https://api.github.com/users/google/repos"

        # Patch GithubOrgClient._public_repos_url as a property
        # using a context manager
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock,
                   return_value=mock_repos_url) as mock_public_repos_url:

            client = GithubOrgClient("google")

            # Call the public_repos method
            result_repos = client.public_repos()

            # Assert that the list of repos matches the expected names
            self.assertEqual(result_repos, expected_repo_names)

            # Assert that _public_repos_url property was accessed once
            mock_public_repos_url.assert_called_once()

            # Assert that get_json was called once with the mocked URL
            mock_get_json.assert_called_once_with(mock_repos_url)


if __name__ == '__main__':
    unittest.main()
