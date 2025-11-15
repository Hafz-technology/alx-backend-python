#!/usr/bin/env python3
"""
Unit test suite for the `client` module.
"""
import unittest
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from typing import Dict, List
from unittest.mock import patch, Mock, PropertyMock
import fixtures  # Import the fixtures


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

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """
        Tests that `GithubOrgClient.public_repos` returns the
        correct list of repo names based on the mocked `repos_payload`.
        """
        # This is the payload that `get_json` will return
        # (simulating the result of `repos_payload`)
        repos_payload = [
            {"name": "repo-one"},
            {"name": "repo-two"},
            {"name": "repo-three"}
        ]
        mock_get_json.return_value = repos_payload

        # This is the URL that `_public_repos_url` will return
        test_repos_url = "https://api.github.com/orgs/test/repos"

        # Patch `_public_repos_url` as a property
        with patch.object(GithubOrgClient,
                          '_public_repos_url',
                          new_callable=PropertyMock) as mock_public_repos_url:

            # Set the return value for the mocked property
            mock_public_repos_url.return_value = test_repos_url

            # Instantiate the client
            client = GithubOrgClient("test")

            # Call the method under test
            public_repos = client.public_repos()

            # Define the expected list of repo names
            expected_repos = ["repo-one", "repo-two", "repo-three"]

            # Assert the list of repos is as expected
            self.assertEqual(public_repos, expected_repos)

            # Assert the mocked property was called once
            mock_public_repos_url.assert_called_once()

            # Assert `get_json` was called once with the correct URL
            # (which came from the mocked property)
            mock_get_json.assert_called_once_with(test_repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self,
                         repo: Dict,
                         license_key: str,
                         expected: bool) -> None:
        """
        Tests the `GithubOrgClient.has_license` static method
        with different repo payloads and license keys.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class([
    {
        "org_payload": fixtures.org_payload,
        "repos_payload": fixtures.repos_payload,
        "expected_repos": fixtures.expected_repos,
        "apache2_repos": fixtures.apache2_repos,
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration test class for `GithubOrgClient`.
    Mocks external requests using fixtures.
    """

    @classmethod
    def setUpClass(cls):
        """
        Sets up the class by patching `requests.get` to return
        example payloads from fixtures.
        """
        # Define the side_effect function for the mock
        def mock_requests_get(url: str):
            """
            Side effect for requests.get. Returns a mock response
            with a .json() method based on the URL.
            """
            mock_resp = Mock()

            # Derive org_url from the repos_url in the fixture
            # e.g., "https.../orgs/google/repos" -> "https.../orgs/google"
            repos_url = cls.org_payload["repos_url"]
            org_url = repos_url.replace("/repos", "")

            if url == org_url:
                mock_resp.json.return_value = cls.org_payload
            elif url == repos_url:
                mock_resp.json.return_value = cls.repos_payload
            else:
                # Return an empty dict for any other unhandled URL
                mock_resp.json.return_value = {}

            return mock_resp

        # Start the patcher
        cls.get_patcher = patch('requests.get', side_effect=mock_requests_get)
        cls.mock_get = cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """
        Stops the class-level patcher after all tests are run.
        """
        cls.get_patcher.stop()
