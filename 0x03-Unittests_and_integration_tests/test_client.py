#!/usr/bin/env python3
"""
Unit tests for the client module.
"""
import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """
    Tests the GithubOrgClient class.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """
        Tests that GithubOrgClient.org returns the correct value
        and that get_json is called once with the expected argument.
        """
        # Define the expected payload for the mocked get_json call
        expected_payload = {"login": org_name, "id": 123}
        mock_get_json.return_value = expected_payload

        # Create an instance of GithubOrgClient
        client = GithubOrgClient(org_name)

        # Access the org property (corrected from method call)
        result = client.org

        # Assert that get_json was called exactly once with the expected URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

        # Assert that the result is equal to the expected payload
        self.assertEqual(result, expected_payload)

    def test_public_repos_url(self):
        """
        Tests that _public_repos_url returns the expected URL
        based on a mocked org payload.
        """
        # Define the payload that GithubOrgClient.org should return
        expected_org_payload = {
            "repos_url": "https://api.github.com/orgs/test_org/repos"}

        # Use patch as a context manager to mock GithubOrgClient.org
        with patch('client.GithubOrgClient.org', new_callable=Mock) as mock:
            mock.return_value = expected_org_payload

            # Create an instance of GithubOrgClient
            client = GithubOrgClient("test_org")

            # Access the _public_repos_url property
            result = client._public_repos_url

            # Assert that GithubOrgClient.org was called
            mock.assert_called_once()

            # Assert that the result is the expected repos_url
            self.assertEqual(result, expected_org_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """
        Tests that GithubOrgClient.public_repos returns the expected
        list of repositories and that the underlying mocked calls are
        made correctly.
        """
        # Define the payload that get_json should return for repos_payload
        mock_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = mock_repos_payload

        # Define the URL that _public_repos_url should return
        expected_public_repos_url ="https://api.github.com/orgs/test_org/repos"

        # Use patch as a context manager to mock GithubOrgClient.
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = expected_public_repos_url

            # Create an instance of GithubOrgClient
            client = GithubOrgClient("test_org")

            # Call the public_repos method
            result = client.public_repos()

            # Assert that _public_repos_url property was accessed
            mock_public_repos_url.assert_called_once()

            # Assert that get_json was called once with the expected URL
            mock_get_json.assert_called_once_with(
                expected_public_repos_url
            )

            # Assert that the list of repos is as expected
            self.assertEqual(result, ["repo1", "repo2", "repo3"])
